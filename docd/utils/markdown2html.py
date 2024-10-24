# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

# Mistune and pygments
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html

class HighlightRenderer(mistune.HTMLRenderer):
    def block_code(self, code, lang=None, info=None):
        if lang is not None:
            lang = lang.strip()
        if lang:
            lexer = get_lexer_by_name(lang,stripall=True)
            formatter = html.HtmlFormatter(
                linenos=False,
                cssclass="highlighted-syntax"
            )
            return highlight(code, lexer, formatter)
        return f"<pre><code>{mistune.escape(code)}</code></pre>"

MARKDOWN = mistune.create_markdown(renderer=HighlightRenderer())

def make_html(text):
    try:
        html = MARKDOWN(text)
        return html
    except TypeError as e:
        print("ISSSUE!!!")
        print(text)
        raise e

