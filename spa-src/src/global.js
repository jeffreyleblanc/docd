// SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
// SPDX-License-Indentifier: MIT

// see https://vuejs.org/guide/reusability/plugins.html#introduction

export const G = {
    install(app, options){
        app.config.globalProperties.$G = this;
    }
};

