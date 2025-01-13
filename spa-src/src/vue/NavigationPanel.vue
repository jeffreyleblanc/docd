<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<nav class="border-r th-core-border-base th-core-bg-surface1">  <!-- Logic and Classes applied in the parent -->
    <header class="p-4 flex flex-col gap-y-4 border-b th-core-border-base">
        <section class="ui-parent-row items-center gap-x-4 th-core-text-pop">
            <h1 class="text-xl font-bold">{{name}}</h1>

            <div class="ui-parent-row items-center gap-x-2">
                <a v-if="home_addr!=''" class="sq-5 cursor-pointer th-accent-text" :href="home_addr" title="go to main homepage">
                    <IconHouse/>
                </a>

                <button v-if="is_darkmode" class="sq-5 cursor-pointer th-accent-text" @click="theme='light'" title="set theme to light">
                    <IconSun/>
                </button>
                <button v-if="!is_darkmode" class="sq-5 cursor-pointer th-accent-text" @click="theme='dark'" title="set theme to dark">
                    <IconMoon/>
                </button>
            </div>

            <div class="grow"/>

            <button class="show-when-mobile-block sq-5" @click="show_nav=false" title="close navigation">
                <IconLargeX/>
            </button>
        </section>
        <section>
            <button @click="open_search_modal">
                Open search
            </button>
        </section>
        <section class="text-sm flex flex-row items-center gap-x-2 th-core-text-base">
            <IconTextRight class="sq-5 th-core-text-muted"/>
            <button class="w-fit p-1 rounded th-core-bg-surface2 th-accent-text" @click="close_all" title="open all categories">
                <IconCaretRight class="sq-3"/>
            </button>
            <button class="w-fit p-1 rounded th-core-bg-surface2 th-accent-text" @click="open_all" title="collapse all categories">
                <IconCaretDown class="sq-3"/>
            </button>
        </section>
    </header>

    <section class="ui-child-expand ui-parent-col ui-scroll-y gap-y-2 px-4 py-8">
        <NavigationPanelCategory
            v-if="root_node!=null"
            :deep="false"
            :node="root_node"
            :current_uri="current_uri"
        />
    </section>
</nav>
</template>

<script>
import IconHouse from "./icons/IconHouse.vue"
import IconSun from "./icons/IconSun.vue"
import IconMoon from "./icons/IconMoon.vue"
import IconMap from "./icons/IconMap.vue"
import IconTextCenter from "./icons/IconTextCenter.vue"
import IconLargeX from "./icons/IconLargeX.vue"
import IconCaretDown from "./icons/IconCaretDown.vue"
import IconCaretRight from "./icons/IconCaretRight.vue"
import IconGeoAltFill from "./icons/IconGeoAltFill.vue"
import IconTextRight from "./icons/IconTextRight.vue"
import NavigationPanelCategory from "./NavigationPanelCategory.vue"

export default {
    data(){ return {} },
    components: {
        IconHouse, IconSun, IconMoon, IconMap, IconTextCenter, IconLargeX,
        IconGeoAltFill, IconTextRight,
        IconCaretDown, IconCaretRight,
        NavigationPanelCategory,
    },
    computed: {
        name(){ return this.$M.data.name },
        home_addr(){ return this.$M.data.home_addr },
        show_nav: {
            get(){ return this.$M.uistate.show_nav; },
            set(val){ this.$M.uistate.show_nav = val; }
        },
        root_node(){ return this.$M.data.root_node; },
        theme: {
            get(){ return this.$M.uistate.theme; },
            set(val){ this.$M.set_theme(val); }
        },
        is_darkmode(){ return this.theme=="dark"; },
        is_mobile(){ return this.$M.uistate.is_mobile; },
        current_uri(){ return this.$M.data.current_uri; },

    },
    methods: {
        // pass
        open_all(){
            this.$M.toggle_all_directories(true);
        },
        close_all(){
            this.$M.toggle_all_directories(false);
        },
        open_search_modal(){
            this.$M.uistate.show_search = true;
        }
    }
}
</script>

