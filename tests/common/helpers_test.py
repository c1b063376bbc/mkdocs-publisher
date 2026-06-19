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

from datetime import datetime
from types import SimpleNamespace

from mkdocs_publisher.common import helpers


def test_ensure_common_config_adds_default_plugin_to_raw_plugin_list():
    mkdocs_config = SimpleNamespace(plugins=["pub-meta"])

    common_config = helpers.ensure_common_config(mkdocs_config=mkdocs_config)

    assert mkdocs_config.plugins == ["pub-common", "pub-meta"]
    assert common_config.date_format == "%Y-%m-%d"
    assert common_config.language == "en"


def test_ensure_common_config_reads_raw_plugin_options():
    mkdocs_config = SimpleNamespace(
        plugins=[
            {
                "pub-common": {
                    "date_format": "%d.%m.%Y",
                    "language": "pl",
                    "translations": {"backlinks_title": "Powiazania"},
                }
            }
        ]
    )

    assert helpers.format_date(value=datetime(2025, 2, 3), mkdocs_config=mkdocs_config) == "03.02.2025"
    assert helpers.get_translation(mkdocs_config=mkdocs_config, key="backlinks_title", default="Backlinks") == (
        "Powiazania"
    )
