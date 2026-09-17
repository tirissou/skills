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
    args = ap.parse_args()

    content = pathlib.Path(args.content).read_text()
    want = args.mermaid == "always" or (args.mermaid == "auto" and 'class="mermaid"' in content)

    out = pathlib.Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(args.title, args.subtitle, args.footer, content, want))

    size = out.stat().st_size
    print(f"{out}  ({size / 1024:.0f} KB, mermaid {'inlined' if want else 'omitted'})")


if __name__ == "__main__":
    main()
