#! /usr/bin/env python3

from pathlib import Path
import markdown

TEMPLATE_ROOT = Path("/usr/local/lib/docd-math")

def make_page(src=None, dest=None):
    assert src is not None

    # Load the template
    template_path = TEMPLATE_ROOT/"template.html"
    HTML_SCAFFOLD = template_path.read_text()

    # Load the markdown source
    mp = Path(src)
    md_src = mp.read_text()

    # Generate the markdown, and replace the math tags
    html1 = markdown.markdown(md_src)
    html1 = html1.replace("<math>","\(").replace("</math>","\)")
    html1 = html1.replace("<mathb>","$$").replace("</mathb>","$$")

    # Generate the page
    page = HTML_SCAFFOLD.replace("PAGE_BODY",html1)
    if dest is None:
        print(page)
    else:
        dest_path = Path(dest)
        with open(dest_path,'w') as f:
            f.write(page)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="Source File")
    parser.add_argument("output", help="Dest File")
    args = parser.parse_args()

    args.src = Path.cwd()/args.src
    args.output = Path.cwd()/args.output

    make_page(args.src,args.output)

if __name__ == '__main__':
    main()

