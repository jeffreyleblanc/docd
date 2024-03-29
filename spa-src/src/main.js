// SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
// SPDX-License-Indentifier: MIT

// CSS Entrypoint
import "./css/index.css"

// Core Javascript and Vue Files
import {createApp} from "vue"
import {G} from "./global.js"
import DataManager from "./DataManager.js"
import MainApp from "./vue/MainApp.vue"

function main(){
    // Get the config
    const config = {
        name: window.$NAME,
        footer_text: window.$FOOTER,
        home_addr: window.$HOME_ADDR
    }

    // Make a data manager
    G.mng = new DataManager(config);

    // Create the main app and mount it
    G.app = createApp(MainApp);
    G.app.use(G);
    G.app.use(G.mng);
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

