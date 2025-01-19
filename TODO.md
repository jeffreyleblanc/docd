# Todo

**SPRINT**

UI

* [ ] Mobile
    * [ ] Add quick search to the mobile bar
    * [ ] Size/position the search modal better in mobile
* [ ] Make the "home" view use the actual index.md/html

Markdown

* [ ] Update the markdown
    * Don't try to guess syntax 

Build System

* [ ] Add back in the export spa/js/css for deployment
    * [ ] be able to run devserver serving the spa and static from `_dist`

Close Out and Deploy

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
