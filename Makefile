# auto generate phony targets
.PHONY: $(shell grep --no-filename -E '^([a-zA-Z_-]|\/)+:' $(MAKEFILE_LIST) | sed 's/:.*//')

dev:
	FLASK_APP=src/app.py flask run --reload

deploy:
	vercel deploy

deploy/production:
	vercel deploy --prod
