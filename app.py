#!/usr/bin/env python3
import json
import time
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

CACHE = {
    "body": None,
    "updated_at": None,
}


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/quotes":
            self.handle_quotes(parsed)
            return
        super().do_GET()

    def handle_quotes(self, parsed):
        query = urllib.parse.parse_qs(parsed.query)
        symbols = query.get("symbols", [""])[0].strip()

        if not symbols:
            self.send_json(400, {"error": "missing symbols"})
            return

        upstream = (
            "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
            + urllib.parse.quote(symbols)
        )

        req = urllib.request.Request(
            upstream,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                )
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            if CACHE["body"] is not None:
                cached = dict(CACHE["body"])
                cached["meta"] = {
                    "stale": True,
                    "source": "cache",
                    "cache_updated_at": CACHE["updated_at"],
                    "upstream_error": str(exc),
                }
                self.send_json(200, cached)
                return

            self.send_json(
                200,
                {
                    "quoteResponse": {"result": [], "error": None},
                    "meta": {
                        "stale": True,
                        "source": "none",
                        "upstream_error": str(exc),
                    },
                },
            )
            return

        body["meta"] = {"stale": False, "source": "yahoo"}
        CACHE["body"] = body
        CACHE["updated_at"] = int(time.time())
        self.send_json(200, body)

    def send_json(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def run():
    server = ThreadingHTTPServer(("0.0.0.0", 8080), DashboardHandler)
    print("Serving dashboard on http://0.0.0.0:8080")
    server.serve_forever()


if __name__ == "__main__":
    run()
