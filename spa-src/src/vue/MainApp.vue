<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div class="ui-spa-root ui-parent-stack font-sans th-core-bg-base th-core-text-base">
    <Article class="ui-child-expand ui-parent-row"/>

    <!-- Transparency used when nav slides out -->
    <div v-show="show_nav" class="show-when-mobile-block ui-child-expand bg-black opacity-75"/>

    <NavigationPanel v-show="show_nav" class="absolute pin-tl ui-parent-col ui-nav-w h-full th-core-bg-base"/>
</div>
</template>

<script>
import NavigationPanel from "./NavigationPanel.vue"
import Article from "./Article.vue"

export default {
    data(){ return {} },
    components: { NavigationPanel, Article },
    computed: {
        show_nav: {
            get(){ return this.$M.uistate.show_nav; },
            set(val){ this.$M.uistate.show_nav = val; }
        }
    },
    methods: {
        // pass
    }
}
</script>

