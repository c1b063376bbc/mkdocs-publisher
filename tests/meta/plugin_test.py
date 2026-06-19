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
from typing import cast
from unittest.mock import patch

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import PluginCollection

from mkdocs_publisher.meta.plugin import MetaPlugin


def test_on_config_can_skip_auto_nav_creation(mkdocs_config: MkDocsConfig):
    meta_plugin = MetaPlugin()
    meta_plugin.load_config(options={"nav": {"enabled": False}})
    mkdocs_config.plugins = cast(PluginCollection, {"pub-meta": meta_plugin})
    mkdocs_config.nav = [{"Manual": "manual.md"}]

    with (
        patch("mkdocs_publisher.meta.plugin.publisher_utils.get_blog_dir", return_value=None),
        patch("mkdocs_publisher.meta.plugin.publisher_utils.get_obsidian_dirs", return_value=([], None)),
        patch.object(meta_plugin._meta_files, "set_configs"),
        patch.object(meta_plugin._meta_files, "add_hidden_path"),
        patch.object(meta_plugin._meta_files, "add_meta_files"),
        patch.object(meta_plugin._meta_files, "drafts", {}),
        patch.object(meta_plugin._meta_files, "hidden", {}),
        patch("mkdocs_publisher.meta.plugin.MetaNav") as meta_nav,
    ):
        meta_nav.return_value.build_nav.return_value = [{"Auto": "auto.md"}]
        config = meta_plugin.on_config(config=mkdocs_config)

    assert config.nav == [{"Manual": "manual.md"}]
    meta_nav.return_value.build_nav.assert_not_called()
