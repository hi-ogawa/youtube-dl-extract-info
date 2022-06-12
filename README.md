# youtube-dl-extract-info

API endpoint exposing [`YoutubeDL.extract_info`](https://github.com/ytdl-org/youtube-dl/blob/9aa8e5340f3d5ece372b983f8e399277ca1f1fe4/youtube_dl/YoutubeDL.py#L774), e.g.

- https://youtube-dl-extract-info-hiro18181.vercel.app/https://www.youtube.com/watch?v=Z5ldO3PJ5IA

for

```py
ydl = YoutubeDL()
ydl.add_default_info_extractors()
ydl.extract_info("https://www.youtube.com/watch?v=Z5ldO3PJ5IA", download=False)
```

## development

```sh
# dependencies
pip install -r requirements.txt

# start server
make dev

# test (note that youtube throttles without "range" header)
curl http://localhost:5000/info?url=Z5ldO3PJ5IA
curl -H 'range: bytes=0-' 'http://localhost:5000/download?url=Z5ldO3PJ5IA&format_id=249' > test.webm
curl -H 'range: bytes=0-' 'https://youtube-dl-extract-info-hiro18181-hiogawa.vercel.app/download?url=Z5ldO3PJ5IA&format_id=249' > test-vercel.webm
```

## deployment

```sh
vercel projects add youtube-dl-extract-info-hiro18181
vercel link -p youtube-dl-extract-info-hiro18181
vercel deploy
vercel deploy --prod
```
