<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div class="ui-spa-root ui-parent-stack font-sans th-core-bg-base th-core-text-base">
    <!-- Main Content Container -->
    <main class="ui-child-expand ui-parent-row">
        <div class="show-when-desktop-block ui-nav-w pl-8 h-full"/>
        <div class="ui-child-expand ui-parent-col">
            <ArticleHeader/>
            <div v-if="error_open" class="py-2 px-4 bg-red-700 text-white">
                {{error_msg}}
            </div>
            <section ref="article_container" class="ui-child-expand ui-parent-col ui-scroll-y">
                <RouterView/>
            </section>
        </div>
    </main>
    <!-- Transparency used when nav slides out -->
    <div v-show="show_nav" class="show-when-mobile-block ui-child-expand bg-black opacity-75"/>
    <!-- Navigation Panel -->
    <NavigationPanel v-show="show_nav" class="absolute pin-tl ui-parent-col ui-nav-w h-full th-core-bg-base"/>
</div>
</template>

<script>
import ArticleHeader from "./ArticleHeader.vue"
import ArticleFooter from "./ArticleFooter.vue"
import NavigationPanel from "./NavigationPanel.vue"

export default {
    data(){ return {} },
    components: { ArticleHeader, ArticleFooter, NavigationPanel },
    computed: {
        show_nav: {
            get(){ return this.$M.uistate.show_nav; },
            set(val){ this.$M.uistate.show_nav = val; }
        },
        error_open(){ return this.$M.uistate.error_open; },
        error_msg(){ return this.$M.uistate.error_msg; }
    }
}
</script>

