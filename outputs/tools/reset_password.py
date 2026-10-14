"""Reset a game account's password (owner tool). The password is typed here, never shown or stored.

Inside Debian, as root, in an interactive terminal:
  python3 reset_password.py <username> [--db swgemu]

How it works: Core3 accepts an account whose salt is empty when the stored password equals the
lowercase-hex SHA-1 of what the client sends (AccountManager::validateAccountCredentials). After
the first successful login the server replaces it with its normal salted SHA-256 (updateHash).
So this sets password = sha1(new password) and salt = '' for one account. No restart is needed.

The server escapes ' " and \\ before hashing, so those characters are refused here.
"""
import getpass, hashlib, re, subprocess, sys


def sql(query, db):
    return subprocess.run(['mariadb', '-N', '-s', db], input=query, text=True,
                          capture_output=True, check=True).stdout.strip()


def main():
    args = sys.argv[1:]
    db = args[args.index('--db') + 1] if '--db' in args else 'swgemu'
    names = [a for i, a in enumerate(args) if a != '--db' and (i == 0 or args[i - 1] != '--db')]
    if len(names) != 1 or not re.fullmatch(r'[A-Za-z0-9_]{1,32}', names[0]) or not re.fullmatch(r'[A-Za-z0-9_]+', db):
        raise SystemExit('usage: reset_password.py <username> [--db swgemu]')
    username = names[0]
    if not sys.stdin.isatty():
        raise SystemExit('Run this in an interactive terminal so the password can be typed privately.')

    account = sql(f"SELECT account_id FROM accounts WHERE username = '{username}';", db)
    if not account:
        raise SystemExit(f'No account named {username} in database {db}.')

    first = getpass.getpass(f'New password for {username}: ')
    second = getpass.getpass('Type it again: ')
    if first != second:
        raise SystemExit('The two entries differ; nothing changed.')
    if len(first) < 6 or not first.isascii() or any(c in first for c in '\'"\\') or any(c.isspace() for c in first):
        raise SystemExit("Use at least 6 plain characters with no spaces, quotes or backslashes; nothing changed.")

    digest = hashlib.sha1(first.encode('ascii')).hexdigest()
    sql(f"UPDATE accounts SET password = '{digest}', salt = '' WHERE account_id = {int(account)};", db)
    print(f'Password for {username} (account {account}) reset. Log in with it; the server re-salts it on first login.')


if __name__ == '__main__':
    main()
