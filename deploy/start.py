"""Start isolated API/OCR/privacy environments; expose only the API port."""
import os
from pathlib import Path
import secrets
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = Path(os.getenv('DATA_DIR', '/var/data'))
    data.mkdir(parents=True, exist_ok=True)
    if os.getuid() == 0:
        os.chown(data, 1000, 1000)
        os.setgroups([])
        os.setgid(1000)
        os.setuid(1000)
    environment = os.environ.copy()
    environment.setdefault('CLAIMS_DB_PATH', str(data / 'claims.sqlite3'))
    environment.setdefault('DEMO_DATA_ROOT', str(data / 'sandboxes'))
    environment.setdefault('ML_MODEL_PATH', str(ROOT / 'models/profile_risk_model.json'))
    environment.setdefault('PAIR_ML_MODEL_PATH', str(ROOT / 'models/pair_risk_model.json'))
    if environment.get('PUBLIC_DEMO_ENABLED', '').lower() == 'true' and not environment.get('DEMO_SESSION_SECRET'):
        raise SystemExit('DEMO_SESSION_SECRET is required for an isolated public demonstration.')
    if environment.get('REQUIRE_META', '').lower() == 'true' and (environment.get('COMPARER') != 'meta' or not environment.get('META_API_KEY')):
        raise SystemExit('Real Meta mode requires COMPARER=meta and META_API_KEY.')
    key = ROOT / 'outputs/evidence-worker.key'
    key.write_text(secrets.token_urlsafe(48), encoding='utf-8')
    key.chmod(0o600)
    children = []
    stopping = False
    last_cleanup = 0
    def stop(*_):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        for executable, module, host, port in [
            ('/opt/privacy/bin/python', 'evidence_tools.privacy_app:app', '127.0.0.1', '8092'),
            ('/opt/vision/bin/python', 'evidence_tools.worker_app:app', '127.0.0.1', '8091'),
            ('/opt/api/bin/python', 'src.web:app', '0.0.0.0', environment.get('PORT', '8090')),
        ]:
            command = [executable, '-m', 'uvicorn', module, '--host', host, '--port', port]
            if host == '0.0.0.0':
                # A managed ingress terminates HTTPS and supplies forwarding headers.
                command += ['--proxy-headers', '--forwarded-allow-ips', '*']
            children.append(subprocess.Popen(command, cwd=ROOT, env=environment))
        while not stopping:
            if time.monotonic() - last_cleanup > 300:
                subprocess.run(['/opt/api/bin/python', '-c', 'from src.demo_sessions import cleanup; cleanup()'], env=environment, check=True)
                last_cleanup = time.monotonic()
            if any(child.poll() is not None for child in children):
                raise RuntimeError('An application process exited; the container must restart.')
            time.sleep(.5)
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=20)
            except subprocess.TimeoutExpired:
                child.kill()


if __name__ == '__main__':
    main()
