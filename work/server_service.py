import signal, subprocess

process = subprocess.Popen(['./core3'], stdin=subprocess.PIPE, start_new_session=True)

def stop(signum, frame):
    if process.poll() is None:
        try:
            process.stdin.write(b'exit\n')
            process.stdin.flush()
        except BrokenPipeError:
            pass

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
raise SystemExit(process.wait())
