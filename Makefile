.PHONY: build

build:
	zola build

build-css:
	lightningcss static/style/*.css --minify --output-dir static/style/min/

watch:
	zola serve && fg
