# Todo

**SPRINT**

Build System

* [ ] Initial code DRY
    * [ ] Make the finding source paths a common method
        * [ ] Add error handling
    * [ ] Make emptying a directory, a common method
    * [ ] Make the spa template handling a common method
* [ ] `spa-dist/` => `spa-framework-dist/`
* [ ] `make-spa-framework` => `developer build-spa-framework`
* [ ] Make a `developer clear-spa-framework`
* [ ] Make a `build-spa` command which will take `spa-dist` and actually put the proper stuff in `DOCS/_dist`
    * [ ] Have it confirm the `spa-dist` isn't empty
* [ ] Enable a uri_base path option, that sets things in the spa template and works with the devserver
* [ ] Make a `build-all` command
* [ ] Make the `push` command work again
    * [ ] Test
    * [ ] Show the caddy fragment needed
* Evaluate what else needs to be done...
    * probably cleaning up usage of DocdRunContext if haven't had to already
    * handle as installed vs not... or save for a next sprint
    * clean up devserver a little, or move some logic out of docd.py
    * etc...

UI

* [ ] Make the "home" view use the actual index.md/html
    * [ ] Make a fallback if it's not there

Markdown

* [ ] Update the markdown
    * Don't try to guess syntax 

Close Out and Deploy

* [ ] Update the dependencies notes
* [ ] Version the search index
* [ ] Enable hosting sites to work with new output using caddy
* [ ] Push as a test
* [ ] Move the branch to master
* [ ] Tag a release and version (in the cli too)
* [ ] Push to github


## Follow On Steps

* [ ] Enable the tornado in dev mode to request a page markdown rebuilt on the fly
    * [ ] basically, if I'm editing the source git file, if I just refresh, get the new one
          without the need to run any cli commands
* update how the markdown gets generated
    * maybe use our nested system as an option
* enable basic editing that for files within git repos
    * optional... only if running as a dev mode
* make the page-build step smarter about only building/copying changes
* add different lunrjs search syntax cheatsheet
* enabled arrows/tab to navigate the search results
