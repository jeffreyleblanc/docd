<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<footer class="flex flex-row items-center justify-center p-8 mt-12 bg-core-950 bg-pink-500 text-core-500 text-sm">
    <span>{{footer_text}}</span>
</footer>
</template>

<script>
export default {
    data(){ return {} },
    computed: {
        footer_text(){ return this.$M.data.footer_text; }
    }
}
</script>

