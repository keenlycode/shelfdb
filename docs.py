import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


docs_src_dir = Path(__file__).parent.joinpath('docs-src')
docs_dest_dir = Path(__file__).parent.joinpath('docs')
template_dir = docs_src_dir.joinpath('template')

template = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
).get_template

for src in docs_src_dir.glob('./template/**/[!_]*.html'):
    src = src.relative_to(template_dir)
    dest = docs_dest_dir.joinpath(src)
    html = template(str(src)).render()
    os.makedirs(str(dest.parent), exist_ok=True)
    dest = open(dest, 'w')
    dest.write(html)
    # print(template(str(src)).render())
