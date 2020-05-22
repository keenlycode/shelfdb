import os
import re
import shutil
from pathlib import Path
import asyncio
from jinja2 import Environment, FileSystemLoader, select_autoescape
from watchgod import awatch, Change


docs_src_dir = Path(__file__).parent.joinpath('docs-src')
docs_dest_dir = Path(__file__).parent.joinpath('docs')
template_dir = docs_src_dir.joinpath('template')

template = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
).get_template


def nodes_modules():
    shutil.copytree(
        'node_modules/bits-ui/dist',
        'docs/static/lib/bits-ui',
        dirs_exist_ok=True)


async def bits_ui_watch():
    src = Path('.').joinpath('docs-src/bits-ui/bits-ui.styl')
    dest = Path('.').joinpath('docs/static/bits-ui/')
    cmd = f'stylus --compress {src} -o {dest}'
    print(cmd)
    await asyncio.create_subprocess_shell(cmd)

    async for changes in awatch(str(src.parent)):
        for change in changes:
            print(change)
            print(cmd)
            await asyncio.create_subprocess_shell(cmd)


def template_to_html(src: 'pathlib.PosfixPath'):
    src = src.relative_to(template_dir)
    dest = docs_dest_dir.joinpath(src)
    print(f'template: {src} -> {dest}')
    html = template(str(src)).render()
    os.makedirs(str(dest.parent), exist_ok=True)
    dest = open(dest, 'w')
    dest.write(html)


async def stylus(src: 'pathlib.Postfixpath'):
    dest = docs_dest_dir.joinpath(src.relative_to(template_dir)).parent
    os.makedirs(dest, exist_ok=True)
    cmd = f'stylus --compress {src} -o {dest}'
    print(cmd)
    await asyncio.create_subprocess_shell(cmd)


async def template_watch():
    for src in template_dir.glob('**/[!_]*.html'):
        template_to_html(src)

    for src in template_dir.glob('**/[!_]*.styl'):
        await stylus(src)

    async for changes in awatch(str(template_dir)):
        for change in changes:
            print(change)
            if (change[0] == Change.modified)\
                    or (change[0] == Change.added):
                if re.match(r'.*\.html$', change[1]):
                    src = Path(change[1])
                    template_to_html(src)
                if re.match(r'.*\.styl$', change[1]):
                    src = Path(change[1])
                    await stylus(src)


async def http_server():
    await asyncio.create_subprocess_shell(
        'python -m http.server --directory docs/')


async def main():
    nodes_modules()
    await asyncio.gather(template_watch(), bits_ui_watch(), http_server())


asyncio.run(main())
