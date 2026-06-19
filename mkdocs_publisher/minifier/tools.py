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

from typing import TYPE_CHECKING

from mkdocs_publisher._shared import file_utils


if TYPE_CHECKING:
    from mkdocs_publisher.minifier.config import MinifierConfig


def get_minifier_tools_versions(minifier_config: "MinifierConfig") -> str:
    tools = {
        "pngquant": [minifier_config.png.pngquant_path, "--version"],
        "oxipng": [minifier_config.png.oxipng_path, "--version"],
        "cjpeg": [minifier_config.jpeg.cjpeg_path, "-version"],
        "djpeg": [minifier_config.jpeg.djpeg_path, "-version"],
        "jpegtran": [minifier_config.jpeg.jpegtran_path, "-version"],
        "svgo": [minifier_config.svg.svgo_path, "--version"],
        "html-minifier-terser": [minifier_config.html.html_minifier_path, "--version"],
        "postcss": [minifier_config.css.postcss_path, "--version"],
        "uglifyjs": [minifier_config.js.uglifyjs_path, "--version"],
    }
    tool_versions = []
    for tool_name, cmd in tools.items():
        try:
            result = file_utils.run_subprocess(cmd=cmd)
        except FileNotFoundError:
            tool_versions.append(f"{tool_name}: missing")
            continue

        output = f"{result.stdout.decode('utf-8')}\n{result.stderr.decode('utf-8')}".strip()
        if result.returncode == 0 and output:
            tool_versions.append(f"{tool_name}: {output.splitlines()[0]}")
        elif result.returncode == 0:
            tool_versions.append(f"{tool_name}: installed")
        else:
            tool_versions.append(f"{tool_name}: missing")
    return "\n".join(tool_versions)
