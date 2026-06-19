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
from types import SimpleNamespace
from unittest.mock import patch

from mkdocs_publisher.offline.plugin import OfflinePlugin


class Response:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    @staticmethod
    def read() -> bytes:
        return b"console.log('offline');"


def test_offline_plugin_downloads_and_replaces_remote_script(tmp_path):
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    plugin = OfflinePlugin()
    plugin.load_config(options={})
    page = SimpleNamespace(file=SimpleNamespace(dest_uri="guide/index.html"))
    config = SimpleNamespace(site_dir=site_dir)

    with patch("mkdocs_publisher.offline.plugin.urlopen", return_value=Response()):
        output = plugin.on_post_page(
            output='<html><head><script src="https://cdn.example.com/app.js"></script></head></html>',
            page=page,
            config=config,
        )

    downloaded_files = list((site_dir / "assets/offline").glob("app-*.js"))
    assert len(downloaded_files) == 1
    assert downloaded_files[0].read_bytes() == b"console.log('offline');"
    assert "../assets/offline/app-" in output
    assert "https://cdn.example.com/app.js" not in output
