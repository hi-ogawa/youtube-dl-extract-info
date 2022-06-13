import asyncio
import socket
import traceback
from typing import Any, Optional
from flask import Flask, request, Response
from youtube_dl import YoutubeDL
import re

from src.http3 import http3_get

app = Flask(__name__)
ydl = YoutubeDL(params=dict(cachedir=False))

#
# middlewares
#


@app.errorhandler(Exception)
def handle_runtime_error(error: Exception):
    full_message = traceback.format_exc()
    print(full_message)
    return (
        dict(
            type=error.__class__.__name__, message=str(error), full_message=full_message
        ),
        400,
    )


@app.after_request
def handle_cors(response: Response) -> Response:
    response.headers.set("access-control-allow-origin", "*")
    response.headers.set("access-control-allow-methods", "GET")
    return response


#
# routes
#


@app.route("/info")
def route_info():
    url = request.args.get("url")
    if url is None:
        raise RuntimeError("invalid url")
    url = fix_vercel_double_slash(url)
    return ydl.extract_info(url, download=False)


@app.route("/download")
def route_download():
    # parse request
    url = request.args.get("url")
    format_id = request.args.get("format_id")
    # NOTE: vercel doesn't support range request/response, so we use url parameters
    range_start = request.args.get("range_start", type=int)
    range_end = request.args.get("range_end", type=int)
    assert url
    assert format_id

    # run extract_info
    url = fix_vercel_double_slash(url)
    info = ydl.extract_info(url, download=False)
    download_url = get_download_url(info, format_id)

    # requests media resource via http3
    req_headers = pick_dict(request.headers, REQ_HEADERS)
    if range_start is not None and range_end is not None:
        req_headers["range"] = f"bytes={range_start}-{range_end}"
    res = asyncio.run(http3_get(download_url, req_headers))

    # respond
    res_headers = pick_dict(res.headers, RES_HEADERS)
    return Response(res.body.getvalue(), headers=res_headers)


REQ_HEADERS = []
RES_HEADERS = ["content-type", "content-length"]


@app.route("/debug")
def route_debug():
    socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    return dict(ok=True)


@app.route("/debug2")
def route_debug2():
    socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return dict(ok=True)


#
# utils
#


def fix_vercel_double_slash(s: str) -> str:
    # workaround vercel's double slash redirection https://github.com/vercel/vercel/issues/3086
    s = re.sub(r"http:\/[^/]", r"http://", s)
    s = re.sub(r"https:\/[^/]", r"https://", s)
    return s


def get_download_url(info: Any, format_id: str) -> Optional[str]:
    formats = info.get("formats")
    assert isinstance(formats, list)
    for format in formats:
        if format.get("format_id") == format_id:
            url = format.get("url")
            assert isinstance(url, str)
            return url
    return None


def pick_dict(d: dict, keys: list[str]) -> dict:
    return {k: d[k] for k in keys if k in d}
