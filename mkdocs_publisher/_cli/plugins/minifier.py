# MIT License
#
# Copyright (c) 2023-2025 Maciej 'maQ' Kusz <maciej.kusz@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path
from typing import Optional

import click

from mkdocs_publisher._shared import file_utils

DEFAULT_CACHE_DIR = ".pub_min_cache"


@click.group
def app():
    """Minifier tools."""
    pass


def _load_minifier_config():
    from mkdocs_publisher.minifier.config import MinifierConfig

    minifier_config = MinifierConfig()
    minifier_config.load_dict({})
    return minifier_config


@app.command()
def tools():
    """Check minifier tools versions."""
    from mkdocs_publisher.minifier.tools import get_minifier_tools_versions

    minifier_config = _load_minifier_config()
    click.echo(get_minifier_tools_versions(minifier_config=minifier_config))


@app.command(name="clean-cache")
@click.option(
    "--cache-dir",
    type=click.Path(file_okay=False, path_type=str),
    default=None,
    help="Minifier cache directory to remove.",
)
@click.option("--yes", is_flag=True, default=False, help="Skip confirmation.")
def clean_cache(cache_dir: Optional[str], yes: bool):
    """Clean minifier cache."""
    cache_path = Path(cache_dir or DEFAULT_CACHE_DIR)
    if not cache_path.exists():
        click.echo(f"Cache directory does not exist: {cache_path}")
        return

    if not yes and not click.confirm(f"Remove minifier cache directory '{cache_path}'?"):
        click.echo("Cache cleanup cancelled.")
        return

    file_utils.remove_dir(directory=cache_path)
    cache_path.rmdir()
    click.echo(f"Removed minifier cache directory: {cache_path}")
