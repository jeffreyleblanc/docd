<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<article class="grow px-4 pt-8 pb-16 md:w-[48rem] md:self-center md:pt-12 md:pb-24 th-core-bg-surface1 docd-article" v-html="current_html" />
</template>

<script>

export default {
    data(){ return {} },
    watch: {
        // When we set a new article, make sure we are at the top
        current_html(new_val,old_val){
            this.$refs.article_container.scrollTop = 0;
        }
    },
    computed: {
        current_html(){ return this.$M.data.current_html; },
    }
}
</script>

