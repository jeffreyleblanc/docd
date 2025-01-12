<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div class="ui-child-expand ui-parent-stack">
    <div class="ui-child-center-x top-[4rem] w-1/2 h-1/2 bg-green-700">
        <input type="text" v-model="local_search_term" class="p-2 text-black"/>
        <button @click="run_search">
            search
        </button>
        <button @click="close">
            CLOSE
        </button>
        <div v-if="has_search_results">
            <span>RESULTS:</span>
            <pre v-for="r in search_results" v-html="JSON.stringify(r)"/>
        </div>
        <div v-else>No results</div>
    </div>
</div>
</template>

<script>

export default {
    data(){ return {
        local_search_term: ""
    }},
    computed: {
        has_search_results(){ return this.$M.data.has_search_result },
        search_results(){ return this.$M.data.search_results }
    },
    methods: {
        run_search(){
            console.log("RUN SEARCH!!",this.local_search_term)
            this.$M.trigger_search(this.local_search_term);
        },
        close(){
            this.$M.uistate.show_search = false;
        }
    }
}
</script>




