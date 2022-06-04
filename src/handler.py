from http.server import BaseHTTPRequestHandler
from urllib.parse import unquote
from youtube_dl import YoutubeDL
import re
import json

ydl = YoutubeDL(params=dict(cachedir=False))
ydl.add_default_info_extractors()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # parse url
        url = unquote(self.path[1:])

        # workaround vercel's double slash redirection https://github.com/vercel/vercel/issues/3086
        url = re.sub(r"http:\/[^/]", r"http://", url)
        url = re.sub(r"https:\/[^/]", r"https://", url)

        try:
            # run youtube-dl
            res = ydl.extract_info(url, download=False)
            status = 200
        except Exception as e:
            res = dict(error_type=e.__class__.__name__, error_message=str(e), url=url)
            status = 400

        # send response
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(res), "utf-8"))
