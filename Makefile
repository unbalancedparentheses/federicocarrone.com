.PHONY: all build build-css watch

NIX_RUN = nix develop --extra-experimental-features 'nix-command flakes' --command

all: build-css build

build:
	$(NIX_RUN) zola build

build-css:
	$(NIX_RUN) lightningcss static/style/*.css --minify --output-dir static/style/min/

watch: build-css
	$(NIX_RUN) zola serve
