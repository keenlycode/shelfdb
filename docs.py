import os
import re
import shutil
from pathlib import Path
import asyncio
import mistune
from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
    evalcontextfunction
)
from watchgod import awatch, Change


docs_src_dir = Path(__file__).parent.joinpath('docs-src')
docs_dest_dir = Path(__file__).parent.joinpath('docs')
template_dir = docs_src_dir.joinpath('template')


def nodes_modules():
    shutil.copytree(
        'node_modules/bits-ui/dist',
        'docs/_static/lib/bits-ui',
        dirs_exist_ok=True)


class BitsUI:
    
    async def run(self):
        src = docs_src_dir.joinpath('_bits-ui/bits-ui.styl')
        dest = docs_dest_dir.joinpath('_static/bits-ui/')
        cmd = f'stylus --compress {src} -o {dest}'
        print(cmd)
        await asyncio.create_subprocess_shell(cmd)

        async for changes in awatch(str(src.parent)):
            for change in changes:
                print(change)
                print(cmd)
                await asyncio.create_subprocess_shell(cmd)


class Template:

    def __init__(self):
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        env.globals['markdown'] = self.markdown
        self.template = env.get_template

    @evalcontextfunction
    def markdown(context, value):
        return 'hi'

    def template_html(self, src: 'pathlib.PosfixPath'):
        src = src.relative_to(template_dir)
        dest = docs_dest_dir.joinpath(src)
        print(f'template: {src} -> {dest}')
        html = self.template(str(src)).render()
        os.makedirs(str(dest.parent), exist_ok=True)
        dest = open(dest, 'w')
        dest.write(html)

    async def stylus(self, src: 'pathlib.Path'):
        dest = docs_dest_dir.joinpath(src.relative_to(template_dir)).parent
        os.makedirs(dest, exist_ok=True)
        cmd = f'stylus --compress {src} -o {dest}'
        print(cmd)
        await asyncio.create_subprocess_shell(cmd)

    async def parcel(self, src):
        dest = docs_dest_dir.joinpath(src.relative_to(template_dir)).parent
        os.makedirs(dest, exist_ok=True)
        cmd = f'parcel build {src} --out-dir {dest}'
        print(cmd)
        await asyncio.create_subprocess_shell(cmd)

    async def run(self):
        for src in template_dir.glob('**/[!_]*.html'):
            self.template_html(src)

        for src in template_dir.glob('**/[!_]*.styl'):
            await self.stylus(src)

        for src in docs_src_dir.glob('**/*.js'):
            await self.parcel(src)

        asset_globs = ['**/*.ico', '**/*.png', '**/*.jpg']
        asset_files = []
        for g in asset_globs:
            asset_files.extend(template_dir.glob(g))

        for src in asset_files:
            dest = src.relative_to(template_dir)
            dest = docs_dest_dir.joinpath(dest)
            shutil.copyfile(src, dest)

        # Copy static files
        shutil.copytree(
            docs_src_dir.joinpath('_static'),
            docs_dest_dir.joinpath('_static'),
            dirs_exist_ok=True)

        async for changes in awatch(str(template_dir)):
            for change in changes:
                print(change)
                if (change[0] == Change.modified)\
                        or (change[0] == Change.added):
                    if re.match(r'.*\.html$', change[1]):
                        src = Path(change[1])
                        self.template_html(src)
                    elif re.match(r'.*\.styl$', change[1]):
                        src = Path(change[1])
                        await self.stylus(src)
                    elif re.match(r'.*\.js$', change[1]):
                        src = Path(change[1])
                        await self.parcel(src)


class HTTPServer:

    async def run(self):
        self.process = await asyncio.create_subprocess_shell(
            'python -m http.server --directory docs/')


async def main():
    nodes_modules()
    global http_server
    http_server = HTTPServer()
    template = Template()
    bits_ui = BitsUI()
    await asyncio.gather(template.run(), bits_ui.run(), http_server.run())

try:
    http_server = None
    asyncio.run(main())
finally:
    http_server.process.terminate()
    print('HTTP server has been terminated')
