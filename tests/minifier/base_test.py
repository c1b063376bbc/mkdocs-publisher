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
from threading import Semaphore
from types import SimpleNamespace

from mkdocs_publisher.minifier.base import BaseMinifier
from mkdocs_publisher.minifier.base import CachedFile
from mkdocs_publisher.minifier.base import MinifierStats


class DummyMinifier(BaseMinifier):
    def are_tools_installed(self) -> bool:
        return True

    def minifier(self, cached_file: CachedFile) -> CachedFile:
        output_file = self._plugin_config.cache_dir / cached_file.cached_file_name
        output_file.write_text("minified", encoding="utf-8")
        return cached_file


def _plugin_config(cache_dir: Path):
    return SimpleNamespace(
        cache_enabled=True,
        cache_dir=cache_dir,
        threads=1,
        exclude=[],
    )


def _mkdocs_config(site_dir: Path):
    return SimpleNamespace(site_dir=site_dir)


def test_minifier_stats_counts_minified_and_cached_files(tmp_path):
    site_dir = tmp_path / "site"
    cache_dir = tmp_path / "cache"
    site_dir.mkdir()
    cache_dir.mkdir()
    site_file = site_dir / "file.txt"
    site_file.write_text("original content", encoding="utf-8")
    cached_files = {}
    stats = MinifierStats()
    minifier = DummyMinifier(
        plugin_config=_plugin_config(cache_dir=cache_dir),
        mkdocs_config=_mkdocs_config(site_dir=site_dir),
        cached_files=cached_files,
        stats=stats,
    )

    minifier._minify_with_cache(file=Path("file.txt"), cache_enabled=True, semaphore=Semaphore(1))

    assert stats.minified_files == 1
    assert stats.cached_files == 0
    assert stats.original_size == len("original content")
    assert stats.minified_size == len("minified")

    site_file.write_text("original content", encoding="utf-8")
    minifier._minify_with_cache(file=Path("file.txt"), cache_enabled=True, semaphore=Semaphore(1))

    assert stats.minified_files == 1
    assert stats.cached_files == 1
    assert stats.original_size == len("original content") * 2
    assert stats.minified_size == len("minified") * 2
    assert round(stats.minification_ratio, 2) == 46.67
