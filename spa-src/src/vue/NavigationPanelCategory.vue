<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<div>
    <template v-if="deep">
        <div>
            <span @click="open=!open"
                class="w-fit py-1 flex flex-row items-center gap-x-2 cursor-pointer th-core-text-base"
            >
                <IconCaretDown v-if="open" class="sq-3 th-accent-text-muted"/>
                <IconCaretRight v-if="!open" class="sq-3 th-accent-text-muted"/>
                <span class="font-semibold th-core-text-pop">{{node.display_name}}</span>
            </span>
        </div>
        <div v-if="open" class="pl-6 flex flex-col">
            <NavigationPanelCategory
                v-for="child in node.directories"
                :key="child.display_name"
                :node="child"
                :deep="true"
                :article_uri="article_uri"
            />

            <div class="border-l pl-4 py-0.5"
                :class="(page.uri==article_uri)?'th-accent-border':'th-core-border-base'"
                v-for="page in node.files"
                :key="page.display_name"
            >
                <span class="cursor-pointer"
                      :class="(page.uri==article_uri)?'th-accent-text font-medium':'th-core-text-muted'"
                      @click="load_page(page)"
                >
                    {{page.display_name}}
                </span>
            </div>
        </div>
    </template>
    <template v-else>
        <div>
            <NavigationPanelCategory
                v-for="child in node.directories"
                :key="child.display_name"
                :node="child"
                :deep="true"
                :article_uri="article_uri"
            />

            <div class="border-l pl-4 py-0.5"
                :class="(page.uri==article_uri)?'th-accent-border':'th-core-border-base'"
                v-for="page in node.files"
                :key="page.display_name"
            >
                <span class="cursor-pointer"
                      :class="(page.uri==article_uri)?'th-accent-text font-medium':'th-core-text-muted'"
                      @click="load_page(page)"
                >
                    {{page.display_name}}
                </span>
            </div>
        </div>
    </template>
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
        node: Object,
        article_uri: String,
        deep: Boolean
    },
    components: { IconChevronRight, IconChevronDown, IconCaretRight, IconCaretDown },
    methods: {
        load_page(page_obj){
            this.$M.load_page(page_obj);
        }
    }
}
</script>

