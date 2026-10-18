"""Chunk-by-chunk jobs for the local model (Claude, 15 Oct 2026): one short, independent request per chunk, which is
what an 8B model does well (the names sweep, proofreading, sorting notes). local_agent.py is for jobs that need to read
several files in one conversation.

    python3 local_map.py --input IN.jsonl --instruction FILE --out DIR [--model M] [--ctx N] [--limit K]
                         [--min-headroom GB] [--reload-every N] [--yield-to-owner]

IN.jsonl has one chunk per line: {"id": "...", "text": "..."}. FILE is the system instruction; the model must answer
with JSON. Each answer goes to DIR/results.jsonl as {"id", "answer"}; a chunk that fails goes to DIR/errors.jsonl and
is tried again on the next run, and chunks already in results.jsonl are skipped, so a run can stop and resume.

Memory (memguard.py): the model is unloaded every --reload-every chunks and at the end (that empties its prompt cache,
which grows in the RAM of whichever PC runs Ollama), and with Ollama on this PC the run pauses when Windows' commit
headroom stays under --min-headroom GB. --yield-to-owner pauses when one of the owner's SWG clients starts (checked
every 10 chunks). Exit codes: 0 all chunks done, 3 paused (memory or the owner; rerun to resume), 1 broken input or
Ollama missing. Nothing leaves the PC except to the Ollama server from ollama_url.pick() (OLLAMA_URL, else the first
server in ollama-url.txt that answers), whose model and context size (at most 16384) are used unless --model/--ctx say.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.request

sys.path.append(str(pathlib.Path(__file__).resolve().parent))  # python -I leaves the script's own folder off sys.path
import memguard
import ollama_url

TASKLIST = '/mnt/c/WINDOWS/system32/tasklist.exe'


def owner_client():
    """True when an SWG client runs on this PC (same test as idle_research.py), None when it can't be told."""
    command = ['tasklist.exe' if sys.platform == 'win32' else TASKLIST, '/FO', 'CSV', '/NH']
    try:
        out = subprocess.run(command, capture_output=True, text=True, errors='replace', timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return bool(re.search(r'(?im)^"(swgclient|swgemu)', out))


def ask(base, model, ctx, instruction, text, timeout=180):
    body = {'model': model, 'stream': False, 'format': 'json', 'think': False, 'keep_alive': '10m',
            # 4096 (was 1536) since 18 Oct: a 20-item item-check answer ran past 1536 tokens and was cut off mid-JSON
            'options': {'temperature': 0, 'num_ctx': ctx, 'num_predict': 4096},
            'messages': [{'role': 'system', 'content': instruction}, {'role': 'user', 'content': text}]}
    request = urllib.request.Request(ollama_url.api('/api/chat', base), json.dumps(body).encode(),
                                     {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content = json.load(response)['message']['content']
    answer = json.loads(content)
    if not isinstance(answer, dict):
        raise ValueError('the answer is not a JSON object')
    return answer


def run(chunks, instruction, out, base, model, ctx, limit=None, min_headroom=memguard.MIN_HEADROOM_GB,
        reload_every=5, yield_to_owner=False, headroom=memguard.commit_headroom_gb, unload=memguard.unload,
        client=owner_client, asker=ask, log=lambda line: print(line, flush=True)):
    """Returns (exit code, summary line). The callables are parameters so the tests can run without Ollama."""
    out.mkdir(parents=True, exist_ok=True)
    results = out / 'results.jsonl'
    done = set()
    if results.exists():
        for line in results.read_text(encoding='utf-8').splitlines():
            try:
                done.add(json.loads(line)['id'])
            except (ValueError, KeyError):
                continue
    todo = [c for c in chunks if c['id'] not in done][:limit]
    local = ollama_url.is_local(base)
    started, errors, attempted, low, code, why = time.time(), 0, 0, None, 0, ''
    with results.open('a', encoding='utf-8') as sink:
        for n, chunk in enumerate(todo, 1):
            if yield_to_owner and n % 10 == 1 and client():
                code, why = 3, "paused: an owner's SWG client is running"
                break
            if n > 1 and (n - 1) % reload_every == 0:
                unload(base, model)
            if local:
                room = headroom()
                if room is not None and room < min_headroom:
                    unload(base, model)
                    time.sleep(5)
                    room = headroom()
                    if room is not None and room < min_headroom:
                        code, why = 3, f'paused: commit headroom {room:.1f} GB < {min_headroom} GB'
                        break
                if room is not None:
                    low = room if low is None else min(low, room)
            attempted += 1
            try:
                answer = asker(base, model, ctx, instruction, chunk['text'])
            except Exception as error:  # noted and retried on the next run
                errors += 1
                with (out / 'errors.jsonl').open('a', encoding='utf-8') as bad:
                    bad.write(json.dumps({'id': chunk['id'], 'error': str(error)[:200]}) + '\n')
                continue
            sink.write(json.dumps({'id': chunk['id'], 'answer': answer}, ensure_ascii=False) + '\n')
            sink.flush()
            if n % 50 == 0:
                log(f'{n}/{len(todo)} chunks, {(time.time() - started) / n:.1f} s each, {errors} errors')
    unload(base, model)
    if code == 0 and errors:
        code, why = 3, f'{errors} chunk(s) failed; rerun to retry them'
    summary = (f'{attempted} of {len(todo)} chunks asked ({len(done)} done before), {errors} errors, '
               f'{(time.time() - started) / 60:.1f} min' + (f', lowest headroom {low:.1f} GB' if low is not None else '')
               + (f'; {why}' if why else ''))
    return code, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--instruction', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--model')
    parser.add_argument('--ctx', type=int)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--min-headroom', type=float, default=memguard.MIN_HEADROOM_GB)
    parser.add_argument('--reload-every', type=int, default=5)
    parser.add_argument('--yield-to-owner', action='store_true')
    args = parser.parse_args()
    try:
        server, skipped = ollama_url.pick()
        model = ollama_url.parse_model(args.model) if args.model else server.model
        ctx = ollama_url.parse_ctx(args.ctx) if args.ctx else min(server.ctx, 16384)
    except ollama_url.OllamaSettingError as error:
        print(f'bad Ollama setting: {error}')
        return 1
    base = server.base
    if skipped:
        print(f'{", ".join(skipped)} not answering; using {ollama_url.describe(base)}')
    try:
        chunks = [json.loads(line) for line in pathlib.Path(args.input).read_text(encoding='utf-8').splitlines()
                  if line.strip()]
        assert all(isinstance(c.get('id'), str) and isinstance(c.get('text'), str) for c in chunks)
        instruction = pathlib.Path(args.instruction).read_text(encoding='utf-8')
    except (OSError, ValueError, AssertionError) as error:
        print(f'bad input: {error}')
        return 1
    code, summary = run(chunks, instruction, pathlib.Path(args.out), base, model, ctx, args.limit, args.min_headroom,
                        max(1, args.reload_every), args.yield_to_owner)
    print(summary)
    return code


if __name__ == '__main__':
    sys.exit(main())
