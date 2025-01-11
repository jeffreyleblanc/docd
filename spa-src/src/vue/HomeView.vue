<template>
<!--
SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
SPDX-License-Indentifier: MIT
-->
<main class="ui-child-expand ui-parent-row">
    <div class="show-when-desktop-block ui-nav-w pl-8 h-full"/>
    <div class="ui-child-expand ui-parent-col">
        <section ref="article_container" class="ui-child-expand ui-parent-col ui-scroll-y">
            <article class="grow px-4 pt-8 pb-16 md:w-[48rem] md:self-center md:pt-12 md:pb-24 th-core-bg-surface1 docd-article">
                <h1 class="text-2xl text-yellow-500">
                    Hello from Home
                </h1>
                <div class="text-purple-300">
                    Why isn't this showing up??
                </div>
            </article>
        </section>
    </div>
</main>
</template>

<script>

export default {
    data(){ return {} },
    // nothing
}
</script>

