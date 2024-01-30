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
	mkdir -p ../support/static
	rm -f ../support/static/*
	cp dist/static/*.css ../support/static/compiled.css
	cp dist/static/*.js  ../support/static/compiled.js
	@# May not support map file since js file name changed
	cp dist/static/*.js.map  ../support/static/
