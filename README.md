# youtube-dl-extract-info

## development

```sh
# dependencies
make pip/dev

# start server
make dev

# test (note that youtube throttles without "range" header)
curl http://localhost:5000/info?url=Z5ldO3PJ5IA
curl 'http://localhost:5000/download?url=Z5ldO3PJ5IA&format_id=249' > test.webm
curl 'https://youtube-dl-extract-info-hiro18181-hiogawa.vercel.app/download?url=Z5ldO3PJ5IA&format_id=249' > test-vercel.webm
```

## deployment

```sh
vercel projects add youtube-dl-extract-info-hiro18181
vercel link -p youtube-dl-extract-info-hiro18181
make deploy
make deploy/production
```

## reference

- https://github.com/hi-ogawa/youtube-dl-web
