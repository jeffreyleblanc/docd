# Todo

**SPRINT**

UI

* [ ] Update the ui in some initially simple ways
    * [ ] Have a top nav bar that works desktop and mobile
    * [ ] Cleanup / Explain the current structure better
    * [ ] Add modal holder for search on desktop
* [ ] Search system
    * [ ] have the search look a bit more like tailwind
        * bar
          [ spyglass 'Quick search... Ctrl K'] => opens modal
          modal
            top [ spy glass  Search docs        [esc]]
            under are the results
            -> make enter trigger
            -> esc closes it
    * [ ] check how that looks/works on mobile
        * there is a spyglass icon, if you click brings up the modal
    * make the search automatic as type, but with a debounce to the enter
        * implement this in the DataManager
    * use https://vuejs.org/guide/essentials/forms.html#trim
* [ ] Cleanup the UI as needed
    * [ ] Article and rendered/raw
        * Also update DataManager parts
    * Determine more updates

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
