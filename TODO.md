# Todo

**SPRINT**

Data

* [x] Add last modified timestamp to the pages database
* [ ] Copy over the raw files into `_resources` as `.txt` files regardless of type

UI

* [ ] Switch to "modern" global store $G pattern vs the $M pattern
* [ ] Update the ui in some initially simple ways
    * [ ] Have a top nav bar that works desktop and mobile
    * [ ] have the search look a bit more like tailwind
        * [ ] check how that looks/works on mobile
* [ ] For each page
    * [ ] Be able to show the raw source as well
    * [ ] Show timestamp for a file
* [ ] vue router
    * [ ] implement it
    * [ ] switch to using non hash addressing

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
