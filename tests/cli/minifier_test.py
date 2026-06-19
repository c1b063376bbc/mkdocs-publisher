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

from unittest.mock import patch

from click.testing import CliRunner

from mkdocs_publisher._cli.plugins.minifier import app


def test_tools_outputs_minifier_tools_versions():
    runner = CliRunner()

    with (
        patch("mkdocs_publisher._cli.plugins.minifier._load_minifier_config", return_value=object()),
        patch("mkdocs_publisher.minifier.tools.get_minifier_tools_versions", return_value="pngquant: missing"),
    ):
        result = runner.invoke(app, ["tools"])

    assert result.exit_code == 0
    assert "pngquant: missing" in result.output


def test_clean_cache_removes_cache_directory(tmp_path):
    runner = CliRunner()
    cache_dir = tmp_path / ".pub_min_cache"
    cache_dir.mkdir()
    (cache_dir / "cached.txt").write_text("cache", encoding="utf-8")

    result = runner.invoke(app, ["clean-cache", "--cache-dir", str(cache_dir), "--yes"])

    assert result.exit_code == 0
    assert not cache_dir.exists()
