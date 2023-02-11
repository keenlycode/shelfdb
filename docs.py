import shutil
from pathlib import Path
import asyncio


async def docs_engrave():
    proc = f'engrave dev docs-src docs --asset --server'
    print(proc)
    proc = await asyncio.create_subprocess_shell(proc)
    await proc.communicate()


async def docs_parcel():
    proc = f"npx parcel watch " +\
        "--dist-dir 'docs' " +\
        "'docs-src/**/*.(js|ts|scss)'"
    print(proc)
    proc = await asyncio.create_subprocess_shell(proc)
    await proc.communicate()


async def main():
    await asyncio.gather(
        docs_engrave(),
        docs_parcel(),
    )


if __name__ == "__main__":
    asyncio.run(main())