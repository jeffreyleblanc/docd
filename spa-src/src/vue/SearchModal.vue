<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div class="ui-child-expand ui-parent-stack">
    <nav class="ui-child-center-x top-[4rem] w-1/2 h-1/2 ui-parent-col th-core-bg-surface2 th-core-text-base rounded-lg">
        <section class="ui-row items-center h-16 border-b th-core-border-soft">
            <div class="sq-4 mx-2">
                <IconSearch/>
            </div>
            <input ref="search_input" type="text" v-model="local_search_term"
                class="flex-1 p-2 bg-transparent border-0 focus:ring-0"
                placeholder="Search documentation"
                @keypress.enter="run_search"
            />
            <div class="ui-row items-center p-2">
                <button @click="close" class="th-core-bg-muted rounded px-2">
                    esc
                </button>
            </div>
        </section>
        <section v-if="has_search_results && search_results.length>0" class="ui-col ui-child-expand ui-scroll-y">
            <template v-for="r in search_results" >
                <RouterLink
                    :to='{name:"pageview",params:{pagepath:r.ref.split("/")}}'
                    class="ui-row items-center px-4 min-h-16 max-h-16 border-b th-core-border-soft hover:th-accent-text hover:th-core-bg-surface3"
                >
                    {{r.ref}}
                </RouterLink>
            </template>
        </section>
        <section v-else class="ui-col ui-child-expand ui-scroll-y">
            <div class="ui-row items-center px-4 min-h-16 max-h-16">
                no results
            </div>
        </section>
        <section class="min-h-8 max-h-8 px-4 ui-row items-center border-t th-core-border-soft text-xs th-core-text-muted">
            <span class="flex-1 h-1"/>
            <span>powered by lunrjs</span>
        </section>
    </nav>
</div>
</template>

<script>
import IconSearch from "./icons/IconSearch.vue"

export default {
    data(){ return {
        local_search_term: ""
    }},
    mounted(){
        // Focus on the search input when mount
        this.$nextTick(()=>{
            this.$refs.search_input.focus();
        });
    },
    components: { IconSearch },
    computed: {
        has_search_results(){ return this.$M.data.has_search_result },
        search_results(){ return this.$M.data.search_results }
    },
    methods: {
        run_search(){
            this.$M.trigger_search(this.local_search_term);
        },
        close(){
            this.$M.close_search_modal();
        }
    }
}
</script>




