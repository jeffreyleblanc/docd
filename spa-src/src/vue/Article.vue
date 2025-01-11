<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div class="th-core-text-muted">
    last modified: {{this.last_modified}}
</div>
<article
    class="grow px-4 pt-8 pb-16 md:w-[48rem] md:self-center md:pt-12 md:pb-24 th-core-bg-surface1 docd-article"
    v-html="current_html"
/>
</template>

<script>

export default {
    data(){ return {} },
    computed: {
        current_html(){ return this.$M.data.current_html; },
        current_node(){ return this.$M.data.current_node; },
        last_modified(){
            return (this.current_node==null)?"":this.current_node.last_modified.split("T")[0];
        }
    }
}
</script>

