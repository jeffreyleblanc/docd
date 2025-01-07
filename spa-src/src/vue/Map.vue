<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<section class="ui-child-expand ui-parent-row">
    <div class="show-when-desktop-block ui-nav-w pl-8 h-full"/>
    <div class="ui-child-expand ui-parent-col gap-y-4 px-8 py-4">
        <nav class="flex flex-row items-center">
            <h1 class="font-bold text-2xl">Site Map</h1>
            <div class="grow"/>
            <button class="sq-5 cursor-pointer" @click="map_open=false" title="close site map">
                <IconLargeX/>
            </button>
        </nav>
        <div
            v-for="category in tmp_entries"
            ref="category_entries"
            :key="category.display_name"
            class="flex flex-col gap-y-4 p-4 rounded th-core-bg-surface1"
        >
            <div class="font-bold text-xl">
                {{category.display_name}}
            </div>
            <div class="columns-2xs gap-y-1">
                <div v-for="page in category.files" :key="page.display_name"
                     class="w-fit cursor-pointer th-core-text-base hover:th-accent-text"
                    @click="load_page(page.uri)"
                >
                    {{page.display_name}}
                </div>
            </div>
        </div>
    </div>
    <!--
    <div>DATA DUMP:</div>
    <pre v-html="JSON.stringify(root_node,null,'    ')"/>
    -->
</section>
</template>

<script>
import IconLargeX from "./icons/IconLargeX.vue"

export default {
    data(){ return {} },
    components: { IconLargeX },
    computed: {
        side_entries(){ return this.$M.data.side_entries; },
        root_node(){ return this.$M.data.root_node; },
        tmp_entries(){ return this.$M.data.root_node.directories; },
        map_open: {
            get(){ return this.$M.uistate.map_open; },
            set(val){ this.$M.uistate.map_open = val; }
        },
    },
    methods: {
        // pass
        load_page(uri){
            this.$M.uistate.map_open = false;
            this.$M.load_page(uri);
        }
    }
}
</script>

