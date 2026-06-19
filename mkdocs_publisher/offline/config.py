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

from mkdocs.config import config_options as option
from mkdocs.config.base import Config


class _OfflineResourceConfig(Config):
    enabled = option.Type(bool, default=True)


class OfflineConfig(Config):
    assets_dir = option.Type(str, default="assets/offline")
    overwrite = option.Type(bool, default=False)
    timeout = option.Type(int, default=10)

    images: _OfflineResourceConfig = option.SubConfig(_OfflineResourceConfig)  # type: ignore
    scripts: _OfflineResourceConfig = option.SubConfig(_OfflineResourceConfig)  # type: ignore
    stylesheets: _OfflineResourceConfig = option.SubConfig(_OfflineResourceConfig)  # type: ignore
