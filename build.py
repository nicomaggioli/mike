"""Inline images into each site template and write the final single-file pages."""
import base64
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
PAGES = [("github.template.html", "index.html"), ("vscode.template.html", "vscode.html")]
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
cache = {}

def inline(match):
    name = match.group(1)
    if name not in cache:
        path = ROOT / "images" / name
        cache[name] = f"data:{MIME[path.suffix.lower()]};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"
    return cache[name]

for src, dst in PAGES:
    template = ROOT / "src" / src
    if not template.exists():
        continue
    html = template.read_text(encoding="utf-8")
    # Pre-render README into the editor so crawlers and no-JS visitors see the pitch (VS Code version).
    m = re.search(r'<template id="tpl-readme">(.*?)</template>', html, re.S)
    html = html.replace("<!--STATIC-README-->", m.group(1).strip() if m else "")
    out = re.sub(r"\{\{IMG:([\w.\-]+)\}\}", inline, html)
    missing = re.findall(r"\{\{[A-Z]+:[^}]*\}\}", out)
    if missing:
        sys.exit(f"{src}: unresolved tokens {missing}")
    (ROOT / dst).write_text(out, encoding="utf-8")
    print(f"Wrote {dst}: {len(out) / 1024:.0f} KB")
