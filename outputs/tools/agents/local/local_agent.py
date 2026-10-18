"""Local stand-in agent (14 Oct 2026, Claude): a small tool loop over Ollama's chat API for the owner's local model.

Why not `codex exec --oss`: Codex 0.162-alpha with Ollama 0.40 cut every reply off after ~260 tokens and had no model
profile for gpt-oss, so tool calls came out in the wrong shape (tests in the 14 Oct board entry). This loop uses Ollama's
own tool calling and is deliberately narrow: three file tools inside ONE workspace folder. No shell, no network, no
paths outside the workspace, so it can't touch /opt/swg, the board or the bots. Claude reviews everything it writes.

    python -I local_agent.py --workspace DIR --task "..." [--model M] [--ctx N] [--max-steps 25] [--ollama-url URL]

Writes DIR/agent-log.jsonl (every request and reply) and prints the final answer. The Ollama server comes from
ollama_url.pick() (OLLAMA_URL, else the first server in ollama-url.txt that answers, else this PC), with that server's
model and context size; --ollama-url, --model and --ctx override them for one run. Every 5 steps, and at the end, the
model is unloaded on whichever PC runs it, because its prompt cache grows in that PC's RAM (memguard.py); the commit
headroom check is for this PC only.
"""
import argparse, json, pathlib, sys, time, urllib.request

sys.path.append(str(pathlib.Path(__file__).resolve().parent))  # python -I leaves the script's own folder off sys.path
import memguard
import ollama_url

READ_CAP = 20000  # characters per read_file call; the model pages with offset
# 18 Oct: on bounty-offers qwen3.6 thought for 856 s (about 200,000 characters) and ended with no tool call and no
# report. A reply is now capped (thinking included), and a run whose task asks for report.md that stops without one is
# asked, at most twice, to write it from what it has read.
MAX_REPLY = 16384  # tokens per reply
NUDGES = 2
NUDGE = ('You have not written report.md yet. Write it now with write_file, from what you have already read. '
         'Keep any further thinking short.')

SYSTEM = (
    'You are a careful assistant working on files in one folder. Use the tools to read files before answering; never '
    'guess file contents. Paths are relative to the folder. Write results only with write_file. When the task is done, '
    'reply with a short plain-text summary of what you wrote and stop calling tools.')

TOOLS = [
    {'type': 'function', 'function': {
        'name': 'list_dir', 'description': 'List files and folders in a folder of the workspace.',
        'parameters': {'type': 'object', 'properties': {'path': {'type': 'string', 'description': 'folder, "." for the top'}},
                       'required': ['path']}}},
    {'type': 'function', 'function': {
        'name': 'read_file', 'description': f'Read a text file; returns up to {READ_CAP} characters from offset.',
        'parameters': {'type': 'object', 'properties': {
            'path': {'type': 'string'}, 'offset': {'type': 'integer', 'description': 'character offset, default 0'}},
            'required': ['path']}}},
    {'type': 'function', 'function': {
        'name': 'write_file', 'description': 'Create or replace a text file in the workspace.',
        'parameters': {'type': 'object', 'properties': {'path': {'type': 'string'}, 'content': {'type': 'string'}},
                       'required': ['path', 'content']}}},
]


def inside(root, rel):
    path = (root / str(rel)).resolve()
    if path != root and root not in path.parents:
        raise ValueError(f'{rel}: outside the workspace')
    return path


def run_tool(root, name, args, protected):
    try:
        if name == 'list_dir':
            folder = inside(root, args.get('path', '.'))
            return '\n'.join(sorted((p.name + ('/' if p.is_dir() else f'  ({p.stat().st_size} bytes)'))
                                    for p in folder.iterdir() if p.name != 'agent-log.jsonl'))
        if name == 'read_file':
            text = inside(root, args['path']).read_text(encoding='utf-8', errors='replace')
            start = int(args.get('offset') or 0)
            chunk = text[start:start + READ_CAP]
            more = f'\n[... {len(text) - start - len(chunk)} more characters; read again with offset {start + len(chunk)}]' \
                if start + len(chunk) < len(text) else ''
            return chunk + more
        if name == 'write_file':
            path = inside(root, args['path'])
            if path in protected:
                return f'refused: {args["path"]} is an input file and must not change'
            path.parent.mkdir(parents=True, exist_ok=True)
            content = str(args.get('content', ''))
            if content and not content.endswith('\n'):
                content += '\n'
            with path.open('w', encoding='utf-8', newline='') as out:   # exactly as given: no CRLF on Windows
                out.write(content)
            return f'wrote {args["path"]} ({len(str(args.get("content", "")))} characters)'
        return f'unknown tool {name}'
    except Exception as error:  # the model sees the error and can correct itself
        return f'error: {error}'


def chat(model, messages, ctx, base=None):
    body = json.dumps({'model': model, 'messages': messages, 'tools': TOOLS, 'stream': False,
                       'options': {'num_ctx': ctx, 'temperature': 0.2, 'num_predict': MAX_REPLY}}).encode()
    request = urllib.request.Request(ollama_url.api('/api/chat', base), body, {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=900) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--task', required=True)
    parser.add_argument('--model', help='default: OLLAMA_MODEL, ollama-model.txt or gpt-oss:20b')
    parser.add_argument('--ctx', type=int, help='context size in tokens; default: OLLAMA_CTX, ollama-ctx.txt or 65536')
    parser.add_argument('--max-steps', type=int, default=25)
    parser.add_argument('--ollama-url', help='Ollama server address; default: OLLAMA_URL, ollama-url.txt or this PC')
    args = parser.parse_args()
    skipped = []
    try:
        if args.ollama_url:
            server = ollama_url.Server(ollama_url.normalize(args.ollama_url), None, None)
        else:
            server, skipped = ollama_url.pick()
    except ollama_url.OllamaUrlError as error:
        parser.error(f'bad Ollama address: {error}')
    except ollama_url.OllamaSettingError as error:
        parser.error(f'bad Ollama setting: {error}')
    base = server.base
    try:
        model = ollama_url.parse_model(args.model) if args.model else server.model or ollama_url.model()
        ctx = ollama_url.parse_ctx(args.ctx) if args.ctx else server.ctx or ollama_url.ctx()
    except ollama_url.OllamaSettingError as error:
        parser.error(f'bad Ollama setting: {error}')
    if skipped:
        print(f'{", ".join(skipped)} not answering; using {ollama_url.describe(base)}')

    root = pathlib.Path(args.workspace).resolve()
    protected = {p.resolve() for p in root.rglob('*') if p.is_file()}  # files present at the start are inputs
    log = (root / 'agent-log.jsonl').open('a', encoding='utf-8')
    messages = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': args.task}]
    started = time.monotonic()
    try:
        return loop(args, root, protected, log, messages, model, ctx, base, started)
    finally:
        memguard.unload(base, model)   # frees the model and its prompt cache for whoever needs that PC next


def loop(args, root, protected, log, messages, model, ctx, base, started):
    local = ollama_url.is_local(base)
    nudges, report = 0, root / 'report.md'
    for step in range(1, args.max_steps + 1):
        if step > 1 and (step - 1) % 5 == 0:   # memguard.py: the prompt cache grows with every request, on any PC
            memguard.unload(base, model)
        if local:   # this PC's commit headroom; another PC's memory can't be read from here
            room = memguard.commit_headroom_gb()
            if room is not None and room < memguard.MIN_HEADROOM_GB:
                memguard.unload(base, model)
                time.sleep(5)
                room = memguard.commit_headroom_gb()
                if room is not None and room < memguard.MIN_HEADROOM_GB:
                    print(f'stopped: Windows commit headroom {room:.1f} GB after {step - 1} steps')
                    return 3
        reply = chat(model, messages, ctx, base)
        message = reply.get('message', {})
        log.write(json.dumps({'step': step, 'reply': message, 'eval_count': reply.get('eval_count'),
                              'prompt_eval_count': reply.get('prompt_eval_count')}) + '\n')
        messages.append(message)
        calls = message.get('tool_calls') or []
        if not calls and 'report.md' in args.task and nudges < NUDGES and not (
                report.exists() and report.stat().st_size > 300):
            nudges += 1
            messages[-1] = {k: v for k, v in message.items() if k != 'thinking'}   # a long thought isn't sent back
            messages.append({'role': 'user', 'content': NUDGE})
            log.write(json.dumps({'step': step, 'nudge': nudges, 'done_reason': reply.get('done_reason')}) + '\n')
            continue
        if not calls:
            print(f'done in {step} steps, {time.monotonic() - started:.0f} s')
            print(message.get('content', '').strip())
            return 0
        for call in calls:
            function = call.get('function', {})
            arguments = function.get('arguments') or {}
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except ValueError:
                    arguments = {}
            result = run_tool(root, function.get('name'), arguments, protected)
            log.write(json.dumps({'step': step, 'tool': function.get('name'), 'args': arguments,
                                  'result': result[:500]}) + '\n')
            messages.append({'role': 'tool', 'tool_name': function.get('name'), 'content': result})
    print(f'stopped: {args.max_steps} steps without a final answer ({time.monotonic() - started:.0f} s)')
    return 1


if __name__ == '__main__':
    sys.exit(main())
