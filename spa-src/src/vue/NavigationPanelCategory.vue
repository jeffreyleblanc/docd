<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div>
    <div>
        <span @click="open=!open"
            class="w-fit py-1 flex flex-row items-center gap-x-2 cursor-pointer th-core-text-base"
        >
            <IconCaretDown v-if="open" class="sq-3 th-accent-text-muted"/>
            <IconCaretRight v-if="!open" class="sq-3 th-accent-text-muted"/>
            <span class="font-semibold th-core-text-pop">{{category.name}}</span>
        </span>
    </div>
    <div v-if="open" class="pl-6 flex flex-col">
        <div class="border-l pl-4 py-0.5"
            :class="(page.uri==article_uri)?'th-accent-border':'th-core-border-base'"
            v-for="page in category.pages"
            :key="page.name"
        >
            <span class="cursor-pointer"
                  :class="(page.uri==article_uri)?'th-accent-text font-medium':'th-core-text-muted'"
                  @click="load_page(page.uri)"
            >
                {{page.name}}
            </span>
        </div>
    </div>
</div>
</template>

<script>
import IconChevronRight from "./icons/IconChevronRight.vue"
import IconChevronDown from "./icons/IconChevronDown.vue"

import IconCaretRight from "./icons/IconCaretRight.vue"
import IconCaretDown from "./icons/IconCaretDown.vue"


export default {
    data(){ return {
        open: true
    } },
    props: {
        category: Object,
        article_uri: String
    },
    components: { IconChevronRight, IconChevronDown, IconCaretRight, IconCaretDown },
    methods: {
        load_page(uri){
            this.$M.load_page(uri);
        }
    }
}
</script>

