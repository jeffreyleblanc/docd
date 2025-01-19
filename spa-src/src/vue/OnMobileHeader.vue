<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<header class="show-when-mobile-flex ui-parent-row items-center gap-x-4 p-4 border-b th-core-border-base th-core-text-pop">
    <button class="sq-6" @click="show_nav=true">
        <IconList/>
    </button>
    <button class="sq-5" @click="open_search_modal">
        <IconSearch/>
    </button>
    <h1 class="text-xl font-bold">{{name}}</h1>
</header>
</template>

<script>
import IconList from "./icons/IconList.vue"
import IconSearch from "./icons/IconSearch.vue"

export default {
    data(){ return {} },
    components: { IconList, IconSearch },
    computed: {
        name(){ return this.$M.data.name },
        show_nav: {
            get(){ return this.$M.uistate.show_nav; },
            set(val){ this.$M.uistate.show_nav = val; }
        }
    },
    methods: {
        open_search_modal(){
            this.$M.open_search_modal();
        }
    }
}
</script>

