import json
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer


def probe(url, timeout=5):
    start = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read(4096).decode("utf-8", "replace")
            return {"ok": True, "status": resp.status, "body": body.strip(),
                    "ms": round((time.time() - start) * 1000)}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}",
                "ms": round((time.time() - start) * 1000)}


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, status=200):
        payload = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            return self._json({"status": "ok"})
        if self.path == "/egress":
            return self._json({
                "public_internet": probe("https://api.ipify.org?format=json"),
                "link_local_metadata": probe(
                    "http://169.254.169.254/latest/meta-data/", timeout=3),
                "ts": time.time(),
            })
        return self._json({"app": "egress-test", "endpoints": ["/health", "/egress"]})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
