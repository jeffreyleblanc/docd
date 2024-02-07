# Code Fragments For Later Use

The following was in the `DataManager.js` constructor.
Since there isn't really a pathway where this event would trigger
independent of the system explicitly setting it, removed.

```js
    // Setup watch for the hashchange
    // ==> Note this pathway to trigger updates is rare
    window.addEventListener("hashchange",(event)=>{
        const url_parts = event.newURL.split("#");
        if(url_parts.length==2){
            const new_page_uri = url_parts[1];
            if(new_page_uri!=this._data.current_uri){
                this.load_page(new_page_uri);
            }
        }
    });
```
