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
            // Names
            name: config.name,
            footer_text: config.footer_text,
            home_addr: config.home_addr,
            // Page Node Data
            root_node: null,
            nodes_by_uri: new Map(),
            orphaned_nodes: new Set(),
            // Current data
            current_uri: "",
            current_html: ""
        });

        this._setup_theme();
    }

    //-- Vue Hooks and Providers --------------------------------------------//

        install(app, options){
            app.config.globalProperties.$M = this;
        }

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

    //-- Data --------------------------------------------//

        async start(){
            // Fetch the database
            await this._fetch_database();

            // Check if we have a current hash and load that
            const curr_hash = document.location.hash;
            if(curr_hash.startsWith("#")){
                const page_uri = curr_hash.substring(1).trim();
                this.load_page_by_uri(page_uri);
            }
        }

        async _fetch_database(){
            const resp = await window.fetch(`db/page-db.json?h=${random_string()}`);
            const objects = await resp.json();
            objects.forEach(e=>this._process_node(e));
        }

        _process_node(node){
            const uri = node.uri;

            // If it's a directory, add containers for children
            if(node.kind == "directory"){
                node.files = [];
                node.directories = [];
            }

            // Save the node by uri
            this._data.nodes_by_uri.set(uri,node);

            // Add to it's parent, or set as orphaned
            if(node.parent_uri){
                const parent = this._data.nodes_by_uri.get(node.parent_uri)||null;
                if(parent==null){
                    this._data.orphaned_nodes.add(node)
                }else{
                    if(node.kind=="file"){
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
            if(node.kind == "directory"){
                for(const orphan of this._data.orphaned_nodes){
                    if(orphan.parent_uri==node.uri){
                        if(orphan.kind=="file"){
                            node.files.push(orphan);
                        }else{
                            node.directories.push(orphan);
                        }
                    }
                    this._data.orphaned_nodes.delete(orphan)
                }
            }
        }

    //-- Page Loading ------------------------------------------------------------------//

        async load_page_by_uri(page_uri){
            try {
                // Close error if open
                this._uistate.error_open = false;

                // Find the page node and get the db_uri
                const page_obj = this._data.nodes_by_uri.get(page_uri);
                const db_uri = page_obj.db_uri;

                // Fetch and set info
                this._data.current_uri = page_uri;
                const resp = await window.fetch(`db/${db_uri}?h=${random_string()}`);
                const text = await resp.text();
                this._data.current_html = text;
            }catch(err){
                console.error("Error loading page:",page_uri,err);
                this._uistate.error_open = true;
                this._uistate.error_msg = `Failed to load ${page_uri}`;
            }

            // Update the hash location
            window.location.hash = page_uri;

            // If we are mobile, make sure to close the nav tray
            if(this._uistate.is_mobile){
                this._uistate.show_nav = false; }
        }

}
