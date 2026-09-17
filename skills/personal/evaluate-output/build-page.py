#!/usr/bin/env python3
"""Splice an HTML content fragment into the shared page shell.

Exists so no agent ever has to reproduce the 3.4 MB Mermaid bundle through its
own context: the library is vendored next to this script and inlined here, and
only when the fragment actually contains a diagram.

    python3 build-page.py --title "Eval: thing" --content frag.html \\
        --out .scratch/thing/visuals/eval-2026-09-16-2107.html

Writes the page, creates parent directories, and prints the absolute path.
"""

import argparse
import pathlib
import re
import sys

SKILL_DIR = pathlib.Path(__file__).resolve().parent
SHELL = SKILL_DIR / "page-shell.html"
MERMAID = SKILL_DIR / "assets" / "mermaid.min.js"

MERMAID_BLOCK = """<script>
{library}
</script>
<script>
  mermaid.initialize({{
    startOnLoad: true,
    theme: window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "default",
    securityLevel: "loose",
  }});
</script>"""


def build(title, subtitle, footer, content, want_mermaid):
    shell = SHELL.read_text()

    mermaid = ""
    if want_mermaid:
        if not MERMAID.exists():
            sys.exit(f"error: the fragment has a .mermaid block but {MERMAID} is missing")
        # A minified bundle can contain the literal "</script" inside a string,
        # which would close the tag early and truncate the library.
        library = MERMAID.read_text().replace("</script", "<\\/script")
        mermaid = MERMAID_BLOCK.format(library=library)

    for token, value in (
        ("<!--TITLE-->", title),
        ("<!--SUBTITLE-->", subtitle),
        ("<!--FOOTER-->", footer),
        ("<!--CONTENT-->", content),
        ("<!--MERMAID-->", mermaid),
    ):
        shell = shell.replace(token, value)
    return shell


def to_artifact(page, title):
    """Strip the document wrapper the Artifact tool supplies itself.

    A published artifact is wrapped in <!doctype html><head></head><body> at
    publish time, so the file must carry page content only. The styles and the
    markup both come from the same shell, so there is one stylesheet to keep.
    """
    style = re.search(r"<style>.*?</style>", page, re.S)
    body = re.search(r"<body>(.*)</body>", page, re.S)
    if not style or not body:
        sys.exit("error: page-shell.html no longer has the <style> and <body> this expects")
    return f"<title>{title}</title>\n{style.group(0)}\n{body.group(1).strip()}\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--footer", default="")
    ap.add_argument("--content", required=True, help="path to the HTML fragment for <main>")
    ap.add_argument("--out", required=True, help="path to write the finished page to")
    ap.add_argument(
        "--mermaid",
        choices=("auto", "always", "never"),
        default="auto",
        help="inline the library: auto inlines only when the fragment has a .mermaid block",
    )
    ap.add_argument(
        "--target",
        choices=("local", "artifact"),
        default="local",
        help="local writes a standalone file; artifact writes page content for the Artifact tool, "
        "which renders mermaid itself and so never needs the library",
    )
    args = ap.parse_args()

    content = pathlib.Path(args.content).read_text()
    want = args.mermaid == "always" or (args.mermaid == "auto" and 'class="mermaid"' in content)
    if args.target == "artifact":
        want = False

    page = build(args.title, args.subtitle, args.footer, content, want)
    if args.target == "artifact":
        page = to_artifact(page, args.title)

    out = pathlib.Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)

    size = out.stat().st_size
    note = "mermaid inlined" if want else "mermaid rendered by the host"
    print(f"{out}  ({size / 1024:.0f} KB, {args.target}, {note})")


if __name__ == "__main__":
    main()
