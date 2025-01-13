<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div class="ui-child-expand ui-parent-stack">
    <div class="ui-child-center-x top-[4rem] w-1/2 h-1/2 ui-parent-col th-core-bg-surface2 th-core-text-base rounded">
        <div class="ui-row items-center p-2 border-b th-core-border-soft">
            <div class="sq-4 mx-2">
                <IconSearch/>
            </div>
            <input type="text" v-model="local_search_term"
                class="flex-1 p-2 bg-transparent border-0 focus:ring-0"
                placeholder="Search documentation"
                @keypress.enter="run_search"
            />
            <div class="ui-row items-center p-2">
                <button @click="close" class="th-core-bg-muted rounded px-2">
                    esc
                </button>
            </div>
        </div>
        <div v-if="has_search_results" class="ui-col">
            <div v-for="r in search_results" class="ui-row items-center px-4 py-2 border-b th-core-border-soft">
                <RouterLink
                    :to='{name:"pageview",params:{pagepath:r.ref.split("/")}}'
                    class="hover:th-accent-text"
                >
                    {{r.ref}}
                </RouterLink>
            </div>
        </div>
        <div v-else>
            waiting...
        </div>
    </div>
</div>
</template>

<script>
import IconSearch from "./icons/IconSearch.vue"

export default {
    data(){ return {
        local_search_term: ""
    }},
    components: { IconSearch },
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




