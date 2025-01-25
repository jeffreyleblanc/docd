<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->

<div class="grow ui-col px-4 pt-4 pb-12 md:w-[48rem] md:self-center th-core-bg-surface1 rounded-lg">
    <div class="ui-row items-center mb-8 text-sm">
        <div class="th-core-text-muted">
            last modified: {{this.last_modified}}
        </div>
        <div class="flex-1"/>
        <div class="ui-row gap-x-2">
            <span class="cursor-pointer" :class="btn_class(!is_raw)" @click="set_rendered">
                rendered
            </span>
            <span>|</span>
            <span class="cursor-pointer" :class="btn_class(is_raw)" @click="load_raw">
                raw
            </span>
        </div>
    </div>
    <!-- Output -->
    <article
        v-if="article_view_mode=='rendered'"
        class="docd-article"
        v-html="current_html"
    />
    <pre v-else class="whitespace-pre-wrap">{{current_raw_text}}</pre>
</div>
</template>
<script>

export default {
    data(){ return {} },
    computed: {
        current_html(){ return this.$M.data.current_html; },
        current_raw_text(){ return this.$M.data.current_raw_text; },
        current_node(){ return this.$M.data.current_node; },
        last_modified(){
            return (this.current_node==null)?"":this.current_node.last_modified.split("T")[0];
        },
        article_view_mode(){ return this.$M.uistate.article_view_mode;  },
        is_raw(){ return (this.article_view_mode=="raw") }
    },
    methods: {
        set_rendered(){
            // Make this not a direct change
            this.$M.uistate.article_view_mode = "rendered";
        },
        load_raw(){
            this.$M.load_raw_text();
        },
        btn_class(is_focus){
            return (is_focus)?'th-accent-text':'th-core-text-muted hover:th-accent-text'
        }
    }
}
</script>

