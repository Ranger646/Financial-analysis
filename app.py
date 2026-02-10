#!/usr/bin/env python3
import json
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler


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
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "missing symbols"}).encode("utf-8"))
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
                body = resp.read()
                status = resp.status
        except Exception as exc:
            self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "upstream fetch failed", "detail": str(exc)}).encode(
                    "utf-8"
                )
            )
            return

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def run():
    server = ThreadingHTTPServer(("0.0.0.0", 8080), DashboardHandler)
    print("Serving dashboard on http://0.0.0.0:8080")
    server.serve_forever()


if __name__ == "__main__":
    run()
