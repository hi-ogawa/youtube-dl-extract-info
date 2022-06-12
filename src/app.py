from typing import Any, Optional
from flask import Flask, request, Response
from youtube_dl import YoutubeDL
import re
import requests

app = Flask(__name__)
ydl = YoutubeDL(params=dict(cachedir=False))

#
# middlewares
#


@app.errorhandler(Exception)
def handle_runtime_error(error: Exception):
    print(error)
    return dict(type=error.__class__.__name__, message=str(error)), 400


@app.after_request
def handle_cors(response: Response) -> Response:
    response.headers.set("access-control-allow-origin", "*")
    response.headers.set("access-control-allow-methods", "GET")
    response.headers.set("access-control-allow-headers", "range")
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
    if url is None or format_id is None:
        raise RuntimeError("invalid url or format_id")

    # run extract_info
    url = fix_vercel_double_slash(url)
    info = ydl.extract_info(url, download=False)
    download_url = get_download_url(info, format_id)

    # requests media resource
    req_headers = pick_dict(request.headers, REQ_HEADERS)

    # respond via iterator
    # - vercel's wrapper (or aws lambda itself) doesn't seem to support streaming response)
    # - also, it looks like it breaks `content-length/content-range` headers
    if False:
        res = requests.get(download_url, headers=req_headers, stream=True)
        res_headers = pick_dict(res.headers, RES_HEADERS)
        res_iter = res.iter_content(chunk_size=ITER_CHUNK_SIZE)
        return Response(res_iter, headers=res_headers)

    res = requests.get(download_url, headers=req_headers)
    res_headers = pick_dict(res.headers, RES_HEADERS)
    return Response(res.content, headers=res_headers)


REQ_HEADERS = ["range"]
RES_HEADERS = ["content-type", "content-length", "content-range", "accept-ranges"]
ITER_CHUNK_SIZE = 2**14

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
