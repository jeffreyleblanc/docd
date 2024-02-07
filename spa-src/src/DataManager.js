// SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
// SPDX-License-Indentifier: MIT

import {reactive} from "vue"
import {random_string} from "./utils.js"

export default class DataManager {

    constructor(config){
        this._uistate = reactive({
            is_mobile: false,
            show_nav: false,
            theme: "light",
            map_open: false,
            error_open: false,
            error_msg: ""
        });

        this._data = reactive({
            name: config.name,
            footer_text: config.footer_text,
            home_addr: config.home_addr,
            side_entries: [],
            article_uri: "",
            article_html: ""
        });

        // Setup watch for the hashchange
        // ==> Note this pathway to trigger updates is rare
        window.addEventListener("hashchange",(event)=>{
            const url_parts = event.newURL.split("#");
            if(url_parts.length==2){
                const new_page_uri = url_parts[1];
                if(new_page_uri!=this._data.article_uri){
                    this.load_page(new_page_uri);
                }
            }
        });
    }

    //-- Vue Hooks and Providers --------------------------------------------//

        install(app, options){
            app.config.globalProperties.$M = this;
        }

        get uistate(){ return this._uistate; }
        get data(){ return this._data; }

    //-- UI --------------------------------------------//

        setup_theme(){
            // https://tailwindcss.com/docs/responsive-design, matches `md:`
            const IS_MOBILE_QUERY = "(min-width:768px)";

            // Setup document resize observer
            const resize_meth = (e)=>{
                const mq = window.matchMedia(IS_MOBILE_QUERY);
                this._uistate.is_mobile = !mq.matches;
                // If not mobile, force showing the nav
                if(!this._uistate.is_mobile){
                    this._uistate.show_nav = true;
                }
            }
            const resizeObserver = new ResizeObserver(e=>{resize_meth(e);});
            resizeObserver.observe(document.body);
            // Trigger once on start
            resize_meth();

            // Sync and setup initial theme
            // Tailwind Note: On page load or when changing themes, best to add inline in `head` to avoid FOUC
            if(localStorage.theme === "dark" || (!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches)){
                this._uistate.theme = "dark";
                document.documentElement.classList.add("dark")
            }else{
                this._uistate.theme = "light";
                document.documentElement.classList.remove("dark")
            }
        }

        set_theme(theme){
            if(theme!="dark" && theme!="light"){
                console.warn(`Unknown theme: ${theme}`); }

            // Set and save the theme
            localStorage.theme = theme;
            this._uistate.theme = theme;
            // // Whenever the user explicitly chooses to respect the OS preference
            // localStorage.removeItem("theme")

            // Apply the change
            (theme=="dark")?
                document.documentElement.classList.add("dark"):
                document.documentElement.classList.remove("dark");
        }

    //-- Data --------------------------------------------//

        async start(){
            // Fetch the database
            await this.fetch_database();

            // Check if we have a current hash and load that
            const curr_hash = document.location.hash;
            if(curr_hash.startsWith("#")){
                const page_uri = curr_hash.substring(1).trim();
                this.load_page(page_uri);
            }
        }

        async fetch_database(){
            const resp = await window.fetch(`db/page-db.json?h=${random_string()}`);
            const page_db_obj = await resp.json();
            console.log("fetch_database:resp",page_db_obj);
            this._data.side_entries = page_db_obj;
        }

        async load_page(page_obj){
            const db_uri = page_obj.db_file_path;
            const page_uri = page_obj.uri
            // => set a loading notice
            try {
                this._uistate.error_open = false;
                this._data.article_uri = page_uri;
                const resp = await window.fetch(`db/${db_uri}?h=${random_string()}`);
                // => clear loading notice
                const text = await resp.text();
                this._data.article_html = text;
            }catch(err){
                console.error("Error loading page:",page_uri,err);
                this._uistate.error_open = true;
                this._uistate.error_msg = `Failed to load ${page_uri}`;
            }

            // Update the hash location
            window.location.hash = page_uri;

            if(this._uistate.is_mobile){
                this._uistate.show_nav = false; }
        }

}
