"""Watch ChatGPT's relay runs like a chat (Claude, 15 Oct 2026; owner: "can we put codex's outputs in a chat window?").

The relay (gpt_relay.ps1) runs `codex exec` and saves the whole transcript to outputs/Agent/relay/<time>-<task>.log.err.
This follows the newest one and prints only GPT's own messages, one short line per command it runs, and the end
(tokens used, the final answer file). It moves to the next run when the relay starts one.

    python -I gpt_chat_view.py            follow live (Ctrl+C to stop)
    python -I gpt_chat_view.py --last     print the newest run once and exit
"""
import glob, os, re, sys, time

RELAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Agent', 'relay')
WIDTH = 110
PLAIN = str.maketrans({'’': "'", '‘': "'", '“': '"', '”': '"', '–': '-', '—': '-', '…': '...'})
WRAPPER = re.compile(r'^"?[A-Za-z]:\\\\WINDOWS\\\\System32\\\\WindowsPowerShell\\\\v1\.0\\\\powershell\.exe"? -Command (.*?)( in [A-Za-z]:\\.*)?$')


def short(cmd):
    """The command GPT ran, without the PowerShell wrapper and the working folder."""
    match = WRAPPER.match(cmd)
    if match:
        cmd = match.group(1).strip()
        if len(cmd) > 1 and cmd[0] in '\'"' and cmd[-1] == cmd[0]:
            cmd = cmd[1:-1]
    return cmd[:WIDTH] + ' ...' if len(cmd) > WIDTH else cmd


def newest():
    runs = sorted(glob.glob(os.path.join(RELAY, '*.log.err')), key=os.path.getmtime)
    return runs[-1] if runs else None


def title(path):
    name = os.path.basename(path)[:-len('.log.err')]   # 20261015-0132-c30-ossus-fauna-server
    stamp, task = name[:13], name[14:]
    return f'== {task}  (started {stamp[9:11]}:{stamp[11:13]}) =='


class Reader:
    """Turns the transcript's blocks (a line 'codex', 'exec', 'user', 'tokens used', then its text) into chat lines."""
    def __init__(self):
        self.block, self.lines = None, []

    def feed(self, line):
        tag = line.strip()
        if tag in ('codex', 'exec', 'user', 'tokens used', 'thinking') and line == tag:
            self.flush()
            self.block = tag
            return
        self.lines.append(line)

    def flush(self):
        text = [l for l in self.lines if l.strip()]
        if self.block == 'codex' and text:
            body = ' '.join(t.strip() for t in text)
            print('GPT: ' + body, flush=True)
        elif self.block == 'exec' and text:
            print('   > ' + short(text[0].strip()), flush=True)
        elif self.block == 'user' and text:
            print('TASK: ' + text[0].strip()[:300] + (' ...' if len(text[0]) > 300 else ''), flush=True)
        elif self.block == 'tokens used' and text:
            print(f'(tokens used: {text[0].strip()})', flush=True)
        self.block, self.lines = None, []


def show(path, follow):
    print('\n' + title(path), flush=True)
    reader = Reader()
    with open(path, encoding='utf-8', errors='replace') as f:
        while True:
            line = f.readline()
            if line:
                reader.feed(line.rstrip('\n').translate(PLAIN))
                continue
            if not follow:
                reader.flush()
                return
            latest = newest()
            if latest and os.path.abspath(latest) != os.path.abspath(path):
                reader.flush()
                answer = path[:-len('.log.err')] + '.md'
                print(f'(run ended; answer: {os.path.basename(answer) if os.path.exists(answer) else "none"})', flush=True)
                return latest
            time.sleep(1)


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    path = newest()
    if not path:
        print('No relay runs yet.')
        return 0
    if '--last' in sys.argv:
        show(path, False)
        return 0
    print('Following ChatGPT\'s relay runs. Ctrl+C to stop.', flush=True)
    while path:
        path = show(path, True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
