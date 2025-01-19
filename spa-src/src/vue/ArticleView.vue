<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div class="flex flex-row gap-x-2">
    <span class="cursor-pointer" @click="set_rendered">
        rendered
    </span>
    <span>|</span>
    <span class="cursor-pointer" @click="load_raw">
        raw
    </span>
</div>
<div class="th-core-text-muted">
    last modified: {{this.last_modified}}
</div>
    <template v-if="article_view_mode=='rendered'">
        <article
            class="grow px-4 pt-8 pb-16 md:w-[48rem] md:self-center md:pt-12 md:pb-24 th-core-bg-surface1 docd-article"
            v-html="current_html"
        />
    </template>
    <template v-else>
        <pre
            class="grow px-4 pt-8 pb-16 md:w-[48rem] md:self-center md:pt-12 md:pb-24 th-core-bg-surface1 whitespace-pre-wrap"
            v-html="current_raw_text"
        />
    </template>
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
        article_view_mode(){ return this.$M.uistate.article_view_mode;  }
    },
    methods: {
        set_rendered(){
            // Make this not a direct change
            this.$M.uistate.article_view_mode = "rendered";
        },
        load_raw(){
            this.$M.load_raw_text();
        }
    }
}
</script>

