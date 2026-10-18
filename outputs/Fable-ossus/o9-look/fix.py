p = 'build_ossus_look.py'
b = open(p, 'rb').read()
i = b.index(b"        line = b'")
j = b.index(b"' + b''.join(bytes(pixels", i)
b = b[:i] + b"        line = b'\x00" + b[j:]
i = b.index(b"        f.write(b'")
j = b.index(b"' + chunk(b'IHDR'", i)
b = b[:i] + b"        f.write(b'\x89PNG\r\n\x1a\n" + b[j:]
assert b'\x00' not in b
open(p, 'wb').write(b)
