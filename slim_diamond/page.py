"""Fills build-log.html's parts and build-guide tabs from BOM.md and BUILD.md, and the guide's contents.

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


# The build guide's contents, grouped: a group opens at its first heading.
GROUPS = {"Tools": "The halves", "Pointing modules": "Pointing modules", "Resetting a closed half": "Both"}


def anchor(text):
    return "b-" + re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def with_ids(html):
    """Each section heading gets an id, for the contents and for links into the guide."""
    return re.sub(r"<h3>(.*?)</h3>", lambda m: f'<h3 id="{anchor(re.sub("<[^>]+>", "", m.group(1)))}">{m.group(1)}</h3>', html)


def contents(html):
    out, open_list = [], False
    for hid, text in re.findall(r'<h3 id="([^"]+)">(.*?)</h3>', html):
        plain = re.sub("<[^>]+>", "", text)
        if plain in GROUPS:
            if open_list:
                out.append("</ol>")
            out += [f"<p>{GROUPS[plain]}</p>", "<ol>"]
            open_list = True
        elif not open_list:
            out.append("<ol>")
            open_list = True
        out.append(f'<li><a href="#{hid}">{text}</a></li>')
    return "\n".join(out + (["</ol>"] if open_list else []))


def fill(page, name, html):
    start, end = f"<!-- {name} -->\n", f"<!-- /{name} -->"
    i, j = page.index(start) + len(start), page.index(end)
    return page[:i] + html + "\n" + page[j:]


def main():
    page = open(PAGE).read()
    bom = convert("BOM.md").replace('href="BUILD.md"', 'href="#build"')   # the guide is a tab on this page
    build = with_ids(convert("BUILD.md"))
    page = fill(page, "BOM.md", bom)
    page = fill(page, "BUILD.md", build)
    page = fill(page, "BUILD.md contents", contents(build))
    open(PAGE, "w").write(page)


if __name__ == "__main__":
    main()
