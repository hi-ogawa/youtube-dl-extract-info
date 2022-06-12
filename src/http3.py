#
# cf. https://github.com/aiortc/aioquic/blob/d272be10b93b09b75325b139090007dae16b9f16/examples/http3_client.py
#

from dataclasses import dataclass
from io import BytesIO
from typing import Deque
from urllib.parse import urlparse

from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3_ALPN, ErrorCode
from aioquic.h3.events import H3Event, HeadersReceived, DataReceived
from aioquic.examples.http3_client import HttpClient


@dataclass
class H3Response:
    body: BytesIO
    headers: dict[str, str]


def make_response(events: Deque[H3Event]) -> H3Response:
    body = BytesIO()
    headers = {}
    for e in events:
        if isinstance(e, HeadersReceived):
            for k, v in e.headers:
                headers[k.decode("utf-8").lower()] = v.decode("utf-8")
        if isinstance(e, DataReceived):
            body.write(e.data)
    return H3Response(body, headers)


async def http3_get(url: str, headers: dict[str, str]) -> H3Response:
    parsed = urlparse(url)
    host = parsed.hostname
    port = 443
    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=H3_ALPN,
    )
    async with connect(
        host,
        port,
        configuration=configuration,
        create_protocol=HttpClient,
    ) as client:
        assert isinstance(client, HttpClient)
        events = await client.get(url, headers)
        response = make_response(events)
        client._quic.close(error_code=ErrorCode.H3_NO_ERROR)
    return response
