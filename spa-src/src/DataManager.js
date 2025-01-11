// SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
// SPDX-License-Indentifier: MIT

import {reactive} from "vue"
import lunr from "lunr"
import {random_string} from "./utils.js"

export default class DataManager {

    constructor(G, config){
        // Access the global
        this.$G = G;

        // Our API URLS
        this.API_URLS = {
            db_root: "/_resources",
            search_index: "/_resources/search/serialized-index.json"
        }

        // Reactive uistate
        this._uistate = reactive({
            is_mobile: false,
            show_nav: false,
            theme: "light",
            error_open: false,
            error_msg: ""
        });

        // Reactive data store
        this._data = reactive({
            // Names
            name: config.name,
            footer_text: config.footer_text,
            home_addr: config.home_addr,
            // Page Node Data
            root_node: null,
            nodes_by_uri: new Map(),
            directory_nodes_by_uri: new Map(),
            orphaned_nodes: new Set(),
            // Current data
            current_uri: "",
            current_html: "",
            current_node: null,
            // Search data
            has_search_result: false,
            search_results: []
        });

        // Track if we've loaded page data or not
        this._page_data_loaded = false;
        this._page_data_loaded_state_hold = null;

        // Track if the search index is loaded
        this._is_search_index_loaded = false;

        // Setup the theme
        this._setup_theme();
    }

    async start(){
        // Fetch the database
        await this._fetch_database();
        this._page_data_loaded = true;

        // If have a state ready, apply it
        if(this._page_data_loaded_state_hold!=null){
            const {name,params} = this._page_data_loaded_state_hold;
            this.load_page_view(name,params);
        }
    }

    //-- Vue Hooks --------------------------------------------//

        get uistate(){ return this._uistate; }
        get data(){ return this._data; }

    //-- UI --------------------------------------------//

        _setup_theme(){
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

        toggle_all_directories(state){
            for(const d of this._data.directory_nodes_by_uri.values()){
                d._is_open = state;
            }
        }

    //-- Data --------------------------------------------//

        async _fetch_database(){
            const resp = await window.fetch(`${this.API_URLS.db_root}/pages-database.json?h=${random_string()}`);
            console.log("DB resp:",resp);
            const objects = await resp.json();
            console.log("DB objs:",objects)
            objects.forEach(e=>this._process_node(e));
        }

        _process_node(node){
            const uri = node.uri;

            // If it's a directory, add containers for children
            if("directory" == node.kind){
                node.files = [];
                node.directories = [];
                node._is_open = true;
            }

            // Save the node by uri
            this._data.nodes_by_uri.set(uri,node);
            if("directory" == node.kind){
                this._data.directory_nodes_by_uri.set(uri,node); }

            // Add to it's parent, or set as orphaned
            if(node.parent_uri){
                const parent = this._data.nodes_by_uri.get(node.parent_uri)||null;
                if(parent==null){
                    this._data.orphaned_nodes.add(node)
                }else{
                    if("file" == node.kind){
                        parent.files.push(node);
                    }else{
                        parent.directories.push(node);
                    }
                }
            }

            // If the uri is ".", set as the root node
            if(uri == "."){
                this._data.root_node = node;
            }

            // Look for orphans that belong
            if("directory" == node.kind){
                for(const orphan of this._data.orphaned_nodes){
                    if(orphan.parent_uri==node.uri){
                        if("file" == orphan.kind){
                            node.files.push(orphan);
                        }else{
                            node.directories.push(orphan);
                        }
                    }
                    this._data.orphaned_nodes.delete(orphan)
                }
            }
        }

    //-- Error System ------------------------------------------------------------------//

        clear_errors(){
            this._uistate.error_open = false;
        }

        set_error(error_msg){
            this._uistate.error_open = true;
            this._uistate.error_msg = error_msg;
        }

    //-- Page Loading ------------------------------------------------------------------//

        async load_page_view(name,params){
            if(!this._page_data_loaded){
                this._page_data_loaded_state_hold = {name,params};
                return;
            }

            const page_uri = params.pagepath.join("/");
            try {
                // Close error if open
                this.clear_errors();

                // Find the page node and get the db_uri
                const page_obj = this._data.nodes_by_uri.get(page_uri);
                const db_uri = page_obj.db_uri;

                this._data.current_node = page_obj;

                // Fetch and set info
                this._data.current_uri = page_uri;
                const resp = await window.fetch(`${this.API_URLS.db_root}/pages-html/${db_uri}?h=${random_string()}`);
                const text = await resp.text();
                this._data.current_html = text;
            }catch(err){
                console.error("Error loading page:",page_uri,err);
                this.set_error(`Failed to load ${page_uri}`);
            }

            // If we are mobile, make sure to close the nav tray
            if(this._uistate.is_mobile){
                this._uistate.show_nav = false; }
        }

    //-- Search System -------------------------------------------------------------------------//

        async load_search_system(){
            // could make a "search_available" uistate
            const resp = await window.fetch(this.API_URLS.search_index);
            const resp_obj = await resp.json();
            this.search_index = lunr.Index.load(resp_obj);
            this._is_search_index_loaded = true;
        }

        async trigger_search(search_text){
            if(! this._is_search_index_loaded){
                await this.load_search_system();
            }
            console.log("run search on:",search_text)
            const results = this.search_index.search(search_text);
            console.log("got:",results)
            this._data.has_search_result = true;
            this._data.search_results = Object.freeze(results);
        }

}
