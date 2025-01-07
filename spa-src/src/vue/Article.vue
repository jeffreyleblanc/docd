<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<main> <!-- Classes applied in the parent -->
    <div class="show-when-desktop-block ui-nav-w pl-8 h-full"/>
    <div class="ui-child-expand ui-parent-col">
        <ArticleHeader/>
        <div v-if="error_open" class="py-2 px-4 bg-red-700 text-white">
            {{error_msg}}
        </div>
        <section ref="article_container" class="ui-child-expand ui-parent-col ui-scroll-y">
            <article class="grow px-4 pt-8 pb-16 md:w-[42rem] md:self-center md:px-0 md:pt-12 md:pb-24 docd-article" v-html="current_html" />
            <ArticleFooter/>
        </section>
    </div>
</main>
</template>

<script>
import ArticleHeader from "./ArticleHeader.vue"
import ArticleFooter from "./ArticleFooter.vue"

export default {
    data(){ return {} },
    components: { ArticleHeader, ArticleFooter },
    watch: {
        // When we set a new article, make sure we are at the top
        current_html(new_val,old_val){
            this.$refs.article_container.scrollTop = 0;
        }
    },
    computed: {
        current_html(){ return this.$M.data.current_html; },
        error_open(){ return this.$M.uistate.error_open; },
        error_msg(){ return this.$M.uistate.error_msg; }
    }
}
</script>

