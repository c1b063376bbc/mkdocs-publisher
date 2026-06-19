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

import subprocess
from unittest.mock import patch

from mkdocs_publisher.debugger import plugin
from mkdocs_publisher.minifier.config import MinifierConfig


def test_get_minifier_tools_versions():
    minifier_config = MinifierConfig()
    minifier_config.load_dict({})

    def run_subprocess(cmd):
        if cmd[0] == "pngquant":
            return subprocess.CompletedProcess(cmd, 0, stdout=b"pngquant 1.0\n", stderr=b"")
        raise FileNotFoundError

    with patch("mkdocs_publisher.debugger.plugin.file_utils.run_subprocess", side_effect=run_subprocess):
        tools_versions = plugin.get_minifier_tools_versions(minifier_config=minifier_config)

    assert "pngquant: pngquant 1.0" in tools_versions
    assert "oxipng: missing" in tools_versions
