# Todo

* paused

## Next Steps (In no order yet)

* [ ] Make the "home" view use the actual index.md/html
    * [ ] Make a fallback if it's not there
* [ ] make the installation methods based on modern python/debian tooling
* [ ] lunr search update
    * not getting common phrases like 'sway'?
    * not adding things from title fields?
* [ ] Version the search index
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
* handle 404 in the spa vue-router for missing pages
* [ ] Evaluate what else needs to be done...
    * probably cleaning up usage of DocdRunContext if haven't had to already
    * handle as installed vs not... or save for a next sprint
    * clean up devserver a little, or move some logic out of docd.py
    * etc...