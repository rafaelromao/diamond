"""Fills build-log.html's BOM and build-guide sections from BOM.md and BUILD.md.

Each document goes between its <!-- NAME --> and <!-- /NAME --> markers, converted to HTML:
its title dropped (the page has its own), its sections one level down, its tables in a
scrolling box. Rerun it whenever either document changes.
"""
import re

import markdown

PAGE = "build-log.html"


def convert(path):
    text = open(path).read()
    text = re.sub(r"\A# .*\n", "", text)                       # the page has its own heading
    html = markdown.markdown(text, extensions=["tables"])
    html = re.sub(r"<(/?)h2>", r"<\1h3>", html)                 # sections under the page's h2
    return html.replace("<table>", '<div class="table"><table>').replace("</table>", "</table></div>")


def main():
    page = open(PAGE).read()
    for name in ("BOM.md", "BUILD.md"):
        start, end = f"<!-- {name} -->\n", f"<!-- /{name} -->"
        i, j = page.index(start) + len(start), page.index(end)
        page = page[:i] + convert(name) + "\n" + page[j:]
    open(PAGE, "w").write(page)


if __name__ == "__main__":
    main()
