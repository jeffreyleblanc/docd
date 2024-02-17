.PHONY: help reset setup build

.DEFAULT=help
help:
	@echo "reset        Clear node_modules"
	@echo "setup        Setup node_modules"
	@echo "build        Build the source"

reset:
	rm -f package-lock.json
	rm -rf node_modules/
	rm -rf dist/

setup:
	npm install

build:
	npx vite build

