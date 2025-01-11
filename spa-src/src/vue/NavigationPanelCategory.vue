<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div>
    <div v-if="deep">
        <span @click="open=!open"
            class="w-fit py-1 flex flex-row items-center gap-x-2 cursor-pointer th-core-text-base"
        >
            <IconCaretDown v-if="open" class="sq-3 th-accent-text-muted"/>
            <IconCaretRight v-if="!open" class="sq-3 th-accent-text-muted"/>
            <span class="font-semibold th-core-text-pop">{{node.display_name}}</span>
        </span>
    </div>
    <div v-if="is_open" :class="(deep)?'pl-6 flex flex-col':''">
        <NavigationPanelCategory
            v-for="child in node.directories"
            :key="child.display_name"
            :node="child"
            :current_uri="current_uri"
        />

        <div class="border-l pl-4 py-0.5"
            :class="(page.uri==current_uri)?'th-accent-border':'th-core-border-base'"
            v-for="page in node.files"
            :key="page.display_name"
        >
            <RouterLink :to='{name:"pageview",params:{pagepath:page.uri.split("/")}}'>
                {{page.display_name}}
            </RouterLink>
        </div>
    </div>
</div>
</template>

<script>
import IconCaretRight from "./icons/IconCaretRight.vue"
import IconCaretDown from "./icons/IconCaretDown.vue"

export default {
    data(){ return {
        // open: true
    } },
    props: {
        deep: {
            type: Boolean,
            default: true
        },
        node: Object,
        current_uri: String
    },
    components: { IconCaretRight, IconCaretDown },
    computed: {
        is_open(){ return (!this.deep)?true:this.open; },
        open: {
            get(){ return this.node._is_open; },
            set(val){ this.node._is_open = val; }
        }
    }
}
</script>

