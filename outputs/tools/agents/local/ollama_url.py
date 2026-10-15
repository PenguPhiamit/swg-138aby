"""Where the project's Ollama server is (Claude, 15 Oct 2026). Every script that calls Ollama asks this module.

Order, first one that is set wins:
  1. the OLLAMA_URL environment variable;
  2. the first line of ollama-url.txt next to this file (gitignored: a LAN address is private; "#" lines are ignored);
  3. http://127.0.0.1:11434, Ollama on this PC.

An address may be written as http://192.168.x.y:11434, or bare as 192.168.x.y (then http:// and port 11434 are added).
Set the variable for one terminal only; the WSL timer (swg-idle-research.timer) never sees a terminal's variables, so
use the file for that. See REMOTE-OLLAMA.md for a server on another PC.
"""
import ipaddress
import os
import urllib.parse
from pathlib import Path

ENV = 'OLLAMA_URL'
DEFAULT = 'http://127.0.0.1:11434'
PORT = 11434
URL_FILE = Path(__file__).resolve().parent / 'ollama-url.txt'


class OllamaUrlError(ValueError):
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


def read_file(path):
    """The address line of ollama-url.txt, or None when the file is missing or holds only comments."""
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    # Windows PowerShell 5.1's ">" and Out-File write UTF-16 with a byte-order mark; Notepad may add a UTF-8 one.
    text = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8-sig', 'replace')
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            return line
    return None


def base_url(environ=None, path=None):
    """The Ollama server's base address (see the module note for the order). Raises OllamaUrlError when it is
    set but unusable, so a typo fails loudly instead of quietly using this PC."""
    environ = os.environ if environ is None else environ
    path = URL_FILE if path is None else path
    value = environ.get(ENV, '').strip()
    source = f'{ENV} variable'
    if not value:
        value, source = read_file(path), path.name
    if not value:
        return DEFAULT
    try:
        return normalize(value)
    except OllamaUrlError as error:
        raise OllamaUrlError(f'{source}: {error}') from None


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


if __name__ == '__main__':
    try:
        url = base_url()
    except OllamaUrlError as error:
        raise SystemExit(f'bad Ollama address: {error}')
    print(f'{url} ({"this PC" if is_local(url) else "another PC"})')
