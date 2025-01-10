# Todo

* [ ] have search only fetch the search-index on the initial grab
* [ ] Unpack what all the current cli do and where things have to live
* [ ] Switch to a tornado based local server system
    * [ ] Keep it simple for now
* [ ] Make a faster basic watcher vite builder
    * [ ] Make it inject the source properly somewhere
* [ ] Switch to "modern" global store $G pattern vs the $M pattern
* [ ] Enable the tornado in dev mode to request a page markdown rebuilt on the fly
    * [ ] basically, if I'm editing the source git file, if I just refresh, get the new one
          without the need to run any cli commands
* [ ] Update the ui in some initially simple ways
    * [ ] Have a top nav bar that works desktop and mobile
    * [ ] have the search look a bit more like tailwind
        * [ ] check how that looks/works on mobile
* [ ] Be able to show the raw source as well
* [ ] Add code files to the search index
    * [ ] this may involve syncing over a set of raw files as well
* [ ] Add timestamp to the files via the actual file timestamps
    * [ ] this may be a json file in the database
* [ ] vue router
    * [ ] implement it
    * [ ] switch to using non hash addressing
* [ ] version the search index
* [ ] enable hosting sites to work with new output using caddy
* [ ] push as a test

PAUSE + EVAL

* update how the markdown gets generated
    * maybe use our nested system as an option
* enable basic editing that for files within git repos
    * optional... only if running as a dev mode
