.PHONY: all build build-css watch

all: build-css build

build:
	zola build

build-css:
	lightningcss static/style/*.css --minify --output-dir static/style/min/

watch:
	zola serve
