<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div class="ui-spa-root ui-parent-stack font-sans th-core-bg-base th-core-text-base">
    <!-- Main Content Container -->
    <main class="ui-child-expand ui-parent-row">
        <!-- When on desktop add column to slide article over to the left -->
        <div class="show-when-desktop-block ui-nav-w pl-8 h-full"/>
        <!-- Main Article Container -->
        <div class="ui-child-expand ui-parent-col">
            <OnMobileHeader/>
            <div v-if="error_open" class="py-2 px-4 bg-red-700 text-white">
                {{error_msg}}
            </div>
            <section ref="article_container" class="ui-child-expand ui-parent-col ui-scroll-y">
                <RouterView/>
                <ArticleFooter/>
            </section>
        </div>
    </main>

    <!-- Transparency used when nav slides out -->
    <div v-show="show_nav" class="show-when-mobile-block ui-child-expand bg-black opacity-75"/>
    <!-- Navigation Panel -->
    <NavigationPanel v-show="show_nav" class="absolute pin-tl ui-parent-col ui-nav-w h-full th-core-bg-base"/>

    <!-- Search Modal -->
    <div v-show="show_search" class="ui-child-expand bg-black opacity-75"/>
    <div v-if="show_search" class="ui-child-expand ui-parent-stack">
        <div class="ui-child-center-x top-[4rem] w-1/2 h-1/2 bg-green-700">
            Search modal
        </div>
    </div>
</div>
</template>

<script>
import OnMobileHeader from "./OnMobileHeader.vue"
import ArticleFooter from "./ArticleFooter.vue"
import NavigationPanel from "./NavigationPanel.vue"

export default {
    data(){ return {} },
    components: { OnMobileHeader, ArticleFooter, NavigationPanel },
    computed: {
        show_nav: {
            get(){ return this.$M.uistate.show_nav; },
            set(val){ this.$M.uistate.show_nav = val; }
        },
        show_search(){ return this.$M.uistate.show_search; },
        error_open(){ return this.$M.uistate.error_open; },
        error_msg(){ return this.$M.uistate.error_msg; },
        current_html(){ return this.$M.data.current_html; },
    },
    watch: {
        // When we set a new article, make sure we are at the top
        current_html(new_val,old_val){
            this.$refs.article_container.scrollTop = 0;
        }
    }
}
</script>

