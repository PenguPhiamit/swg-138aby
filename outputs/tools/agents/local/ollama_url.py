"""Where the project's Ollama server is, and which model it runs (Claude, 15 Oct 2026). Every script that calls Ollama
asks this module. Three settings, each with the same order, first one that is set wins:

                 environment variable   file next to this one (gitignored)   default
  address        OLLAMA_URL             ollama-url.txt                       http://127.0.0.1:11434
  model          OLLAMA_MODEL           ollama-model.txt                     gpt-oss:20b
  context size   OLLAMA_CTX             ollama-ctx.txt                       65536 (tokens)

A file holds one line ("#" lines are ignored). An address may be written as http://192.168.x.y:11434, or bare as
192.168.x.y (then http:// and port 11434 are added). Set a variable for one terminal only; the WSL timer
(swg-idle-research.timer) never sees a terminal's variables, so use the files for that. See REMOTE-OLLAMA.md for a
server on another PC and for choosing a smaller model.

Several servers, with a fallback (17 Oct): ollama-url.txt may list one server per line, in order of preference, each
optionally followed by the model and the context size to use there:

    http://192.168.x.y:11434   qwen3.6:35b-a3b   65536      # the friend's PC
    127.0.0.1                  qwen3:8b          16384      # this PC, when the friend's PC is off

pick() returns the first that answers /api/tags within PROBE_S seconds (the last one is not probed: callers find out).
A line without a model or size takes OLLAMA_MODEL / ollama-model.txt and OLLAMA_CTX / ollama-ctx.txt, and those two
variables beat every line. The OLLAMA_URL variable means exactly one server, with no fallback.

    python3 ollama_url.py     # shows what a script would use now
"""
import ipaddress
import json
import os
import re
import urllib.parse
import urllib.request
from collections import namedtuple
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV, URL_FILE, DEFAULT = 'OLLAMA_URL', HERE / 'ollama-url.txt', 'http://127.0.0.1:11434'
ENV_MODEL, MODEL_FILE, DEFAULT_MODEL = 'OLLAMA_MODEL', HERE / 'ollama-model.txt', 'gpt-oss:20b'
ENV_CTX, CTX_FILE, DEFAULT_CTX = 'OLLAMA_CTX', HERE / 'ollama-ctx.txt', 65536
PORT = 11434
CTX_RANGE = (2048, 2_097_152)
MODEL_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:/@+-]*')
PROBE_S = 3   # a server on the home network answers /api/tags in milliseconds; an off PC never does

Server = namedtuple('Server', 'base model ctx')


class OllamaSettingError(ValueError):
    pass


class OllamaUrlError(OllamaSettingError):
    pass


def normalize(text):
    """The base address ("http://host:port", no trailing slash) for what the owner wrote, or OllamaUrlError."""
    text = text.strip()
    if not text:
        raise OllamaUrlError('empty address')
    bare = '://' not in text
    parts = urllib.parse.urlsplit('http://' + text if bare else text)
    if parts.scheme not in ('http', 'https'):
        raise OllamaUrlError(f'{parts.scheme}:// is not supported (use http:// or https://)')
    if '@' in parts.netloc:
        raise OllamaUrlError('no user name or password in the address (Ollama has none)')
    try:
        host, port = parts.hostname, parts.port
    except ValueError as error:
        raise OllamaUrlError(f'bad port ({error})') from None
    if not host:
        raise OllamaUrlError('no host name in the address')
    if parts.query or parts.fragment:
        raise OllamaUrlError('give the server address only, without ? or #')
    path = parts.path.rstrip('/')
    if path == '/api' or path.startswith('/api/'):
        raise OllamaUrlError('give the server address only, without /api/...')
    if bare and port is None:
        port = PORT
    shown = f'[{host}]' if ':' in host else host
    return f'{parts.scheme}://{shown}' + (f':{port}' if port else '') + path


def parse_model(text):
    """A model name as Ollama spells it (qwen3:8b, gpt-oss:20b, hf.co/user/repo:Q4_K_M), or OllamaSettingError."""
    text = text.strip()
    if not MODEL_NAME.fullmatch(text):
        raise OllamaSettingError(f'"{text}" is not a model name (like qwen3:8b: letters, digits and . _ : / @ + -)')
    return text


def parse_ctx(text):
    """A context size in tokens, or OllamaSettingError."""
    try:
        value = int(str(text).strip())
    except ValueError:
        raise OllamaSettingError(f'"{str(text).strip()}" is not a whole number of tokens (like 32768)') from None
    if not CTX_RANGE[0] <= value <= CTX_RANGE[1]:
        raise OllamaSettingError(f'{value} tokens is outside {CTX_RANGE[0]}..{CTX_RANGE[1]}')
    return value


def read_lines(path):
    """The value lines of a settings file ("#" comments dropped, also after a value); [] when the file is missing."""
    try:
        raw = path.read_bytes()
    except OSError:
        return []
    # Windows PowerShell 5.1's ">" and Out-File write UTF-16 with a byte-order mark; Notepad may add a UTF-8 one.
    text = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8-sig', 'replace')
    lines = (re.split(r'\s#', line, maxsplit=1)[0].strip() for line in text.splitlines())
    return [line for line in lines if line and not line.startswith('#')]


def read_file(path):
    """The first value line of a settings file, or None when the file is missing or holds only comments."""
    lines = read_lines(path)
    return lines[0] if lines else None


def setting(env_name, path, default, parse, environ=None):
    """The value for one setting (see the module note for the order). Raises OllamaSettingError when it is set but
    unusable, so a typo fails loudly instead of quietly using the default."""
    environ = os.environ if environ is None else environ
    value = environ.get(env_name, '').strip()
    source = f'{env_name} variable'
    if not value:
        value, source = read_file(path), path.name
    if not value:
        return default
    try:
        return parse(value)
    except OllamaSettingError as error:
        raise type(error)(f'{source}: {error}') from None


def base_url(environ=None, path=None):
    """The first configured server's address. pick() is the one to use: it falls back when that server is off."""
    return servers(environ, path)[0].base


def parse_line(line, where):
    """Server parts (base, model or None, ctx or None) from one line of ollama-url.txt: an address, then optionally a
    model name and a context size in either order."""
    words = line.split()
    if len(words) > 3:
        raise OllamaSettingError(f'{where}: "{line}" holds more than an address, a model and a context size')
    try:
        base = normalize(words[0])
    except OllamaUrlError as error:
        raise OllamaUrlError(f'{where}: {error}') from None
    name = size = None
    for word in words[1:]:
        try:
            if word.isdigit():
                if size is not None:
                    raise OllamaSettingError('two context sizes')
                size = parse_ctx(word)
            elif name is None:
                name = parse_model(word)
            else:
                raise OllamaSettingError('two model names')
        except OllamaSettingError as error:
            raise OllamaSettingError(f'{where}: {error}') from None
    return base, name, size


def servers(environ=None, path=None):
    """Every configured server as Server(base, model, ctx), in order of preference (see the module note). Raises
    OllamaSettingError (OllamaUrlError for an address) naming its source, so a typo fails loudly."""
    environ = os.environ if environ is None else environ
    path = URL_FILE if path is None else path
    if environ.get(ENV, '').strip():
        return [Server(setting(ENV, path, DEFAULT, normalize, environ), model(environ), ctx(environ))]
    lines = read_lines(path)
    if not lines:
        return [Server(DEFAULT, model(environ), ctx(environ))]
    forced_model, forced_ctx = environ.get(ENV_MODEL, '').strip(), environ.get(ENV_CTX, '').strip()
    out = []
    for n, line in enumerate(lines, 1):
        base, name, size = parse_line(line, f'{path.name} line {n}')
        out.append(Server(base, model(environ) if forced_model or not name else name,
                          ctx(environ) if forced_ctx or size is None else size))
    return out


def answers(base, timeout=PROBE_S):
    """True when an Ollama server answers /api/tags at base within timeout seconds."""
    try:
        with urllib.request.urlopen(api('/api/tags', base), timeout=timeout) as response:
            response.read()
        return True
    except (OSError, ValueError):
        return False


def pick(environ=None, path=None, probe=None):
    """(the Server to use, [host:port of each server listed before it that did not answer]). A single server is
    returned without a probe, as before; with several, the first that answers wins and the last is the fallback."""
    probe = answers if probe is None else probe
    listed = servers(environ, path)
    skipped = []
    for server in listed[:-1]:
        if probe(server.base):
            return server, skipped
        skipped.append(describe(server.base))
    return listed[-1], skipped


def model(environ=None, path=None):
    """The model every script asks for."""
    return setting(ENV_MODEL, MODEL_FILE if path is None else path, DEFAULT_MODEL, parse_model, environ)


def ctx(environ=None, path=None):
    """The context window (tokens) every script asks for."""
    return setting(ENV_CTX, CTX_FILE if path is None else path, DEFAULT_CTX, parse_ctx, environ)


def api(route, base=None):
    """Full address of an API route, for example api('/api/chat')."""
    return (base_url() if base is None else base).rstrip('/') + '/' + route.lstrip('/')


def is_local(base):
    """True when the address is this PC (loopback). WSL runs in mirrored networking, so 127.0.0.1 there is Windows'."""
    host = (urllib.parse.urlsplit(base).hostname or '').lower()
    if host == 'localhost' or host.endswith('.localhost'):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    ip = getattr(ip, 'ipv4_mapped', None) or ip
    return ip.is_loopback or ip.is_unspecified


def describe(base):
    """host:port for messages (never credentials; normalize() refuses them)."""
    parts = urllib.parse.urlsplit(base)
    return f'{parts.hostname}:{parts.port or (443 if parts.scheme == "https" else 80)}'


def model_missing(tags_body, wanted):
    """Why `wanted` is not on the server, from the body of its /api/tags answer; None when it is there or the answer
    can't be read (an unreadable answer is not a reason to hold work back)."""
    try:
        names = {m.get('name') or m.get('model') for m in json.loads(tags_body).get('models') or []}
    except (ValueError, AttributeError, TypeError):
        return None
    if wanted in names or (':' not in wanted and f'{wanted}:latest' in names):
        return None
    return f'model {wanted} is not on the server (ollama pull {wanted})'


if __name__ == '__main__':
    try:
        listed = servers()
        chosen, skipped = pick()
    except OllamaSettingError as error:
        raise SystemExit(f'bad Ollama setting: {error}')
    for server in listed:
        mark = 'use' if server == chosen else 'off' if describe(server.base) in skipped else '   '
        print(f'{mark} {server.base} ({"this PC" if is_local(server.base) else "another PC"}), model {server.model}, '
              f'context {server.ctx}')
