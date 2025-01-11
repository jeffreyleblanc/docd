// SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
// SPDX-License-Indentifier: MIT

// CSS Entrypoint
import "./css/index.css"

// Core Javascript and Vue Files
import {createApp} from "vue"
import { createWebHistory, createRouter } from "vue-router"
import {G} from "./global.js"
import DataManager from "./DataManager.js"
import MainApp from "./vue/MainApp.vue"

import HomeView from "./vue/HomeView.vue"
import Article from "./vue/Article.vue"

function main(){
    // Get the config
    const config = {
        name: window.$NAME,
        footer_text: window.$FOOTER,
        home_addr: window.$HOME_ADDR
    }

    // Make a data manager
    G.mng = new DataManager(G,config);

    const routes = [
        { name: "home", path: "/", component: HomeView },
        // see https://router.vuejs.org/guide/essentials/route-matching-syntax#Repeatable-params
        { name: "pageview", path: "/view/:pagepath+", component: Article },
    ]

    G.router = createRouter({
        history: createWebHistory(),
        routes,
    })

    // Wire the path logic here so we pickup initial state
    G.router.beforeEach((to,from)=>{
        const {name,params} = to;
        console.log("ROUTER:from",from)
        console.log("ROUTER::to",name,params)
        if("home" == name){
            // pass
        }
        else if("pageview" == name){
            console.log("ROUTER::to",name,params)
            // LOAD THE PAGE
            // G.mng.load_page_by_uri(params.pagepath.join("/"));
            G.mng.load_page_by_uri(name,params);
        }
    })

    // Create the main app and mount it
    G.app = createApp(MainApp);
    G.app.use(G);
    G.app.use(G.router)
    G.app.mount("#mount");

    // Start
    G.mng.start();

    // Export to window for debugging
    if(window.$G===undefined){
        window.$G = G;
    }else{
        console.warn("window.$G already assigned.")
    }
}

main();

