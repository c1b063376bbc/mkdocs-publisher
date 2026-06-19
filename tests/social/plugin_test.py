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

import pytest
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File
from mkdocs.structure.pages import Page

from mkdocs_publisher.social.plugin import SocialPlugin

HTML = "<html><head></head><body><p>Page</p></body></html>"


def _page(mkdocs_config: MkDocsConfig, path: str = "index.md") -> Page:
    page = Page(
        title="Page",
        file=File(
            path=path,
            src_dir=mkdocs_config.docs_dir,
            dest_dir=mkdocs_config.site_dir,
            use_directory_urls=True,
        ),
        config=mkdocs_config,
    )
    page.meta = {"title": "Title", "description": "Description"}
    return page


@pytest.mark.parametrize(
    "plugin_options,page_meta,path",
    [
        ({"ignore": {"patterns": ["drafts/*"]}}, {}, "drafts/page.md"),
        ({}, {"social": False}, "index.md"),
    ],
)
def test_social_properties_can_be_ignored(
    mkdocs_config: MkDocsConfig,
    plugin_options: dict,
    page_meta: dict,
    path: str,
):
    plugin = SocialPlugin()
    plugin.load_config(options=plugin_options)
    page = _page(mkdocs_config=mkdocs_config, path=path)
    page.meta.update(page_meta)

    output = plugin.on_post_page(output=HTML, page=page, config=mkdocs_config)

    assert output == HTML


def test_social_properties_are_added_by_default(mkdocs_config: MkDocsConfig):
    plugin = SocialPlugin()
    plugin.load_config(options={})
    page = _page(mkdocs_config=mkdocs_config)

    output = plugin.on_post_page(output=HTML, page=page, config=mkdocs_config)

    assert 'property="og:title"' in output
    assert 'property="twitter:title"' in output
