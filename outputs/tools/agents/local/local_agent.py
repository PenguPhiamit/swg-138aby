"""Local stand-in agent (14 Oct 2026, Claude): a small tool loop over Ollama's chat API for the owner's local model.

Why not `codex exec --oss`: Codex 0.162-alpha with Ollama 0.40 cut every reply off after ~260 tokens and had no model
profile for gpt-oss, so tool calls came out in the wrong shape (tests in the 14 Oct board entry). This loop uses Ollama's
own tool calling and is deliberately narrow: three file tools inside ONE workspace folder. No shell, no network, no
paths outside the workspace, so it can't touch /opt/swg, the board or the bots. Claude reviews everything it writes.

    python -I local_agent.py --workspace DIR --task "..." [--model gpt-oss:20b] [--max-steps 25] [--ollama-url URL]

Writes DIR/agent-log.jsonl (every request and reply) and prints the final answer. The Ollama address comes from
ollama_url.py (OLLAMA_URL, then ollama-url.txt, then this PC); --ollama-url overrides it for one run.
"""
import argparse, json, pathlib, sys, time, urllib.request

sys.path.append(str(pathlib.Path(__file__).resolve().parent))  # python -I leaves the script's own folder off sys.path
import ollama_url

READ_CAP = 20000  # characters per read_file call; the model pages with offset

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
                       'options': {'num_ctx': ctx, 'temperature': 0.2}}).encode()
    request = urllib.request.Request(ollama_url.api('/api/chat', base), body, {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=900) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--task', required=True)
    parser.add_argument('--model', default='gpt-oss:20b')
    parser.add_argument('--ctx', type=int, default=65536)
    parser.add_argument('--max-steps', type=int, default=25)
    parser.add_argument('--ollama-url', help='Ollama server address; default: OLLAMA_URL, ollama-url.txt or this PC')
    args = parser.parse_args()
    try:
        base = ollama_url.normalize(args.ollama_url) if args.ollama_url else ollama_url.base_url()
    except ollama_url.OllamaUrlError as error:
        parser.error(f'bad Ollama address: {error}')

    root = pathlib.Path(args.workspace).resolve()
    protected = {p.resolve() for p in root.rglob('*') if p.is_file()}  # files present at the start are inputs
    log = (root / 'agent-log.jsonl').open('a', encoding='utf-8')
    messages = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': args.task}]
    started = time.monotonic()
    for step in range(1, args.max_steps + 1):
        reply = chat(args.model, messages, args.ctx, base)
        message = reply.get('message', {})
        log.write(json.dumps({'step': step, 'reply': message, 'eval_count': reply.get('eval_count'),
                              'prompt_eval_count': reply.get('prompt_eval_count')}) + '\n')
        messages.append(message)
        calls = message.get('tool_calls') or []
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
