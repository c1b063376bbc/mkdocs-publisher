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

from types import SimpleNamespace

from mkdocs_publisher.rss.plugin import RssPlugin


def _page(src_path: str, url: str, title: str, date: str):
    return SimpleNamespace(
        file=SimpleNamespace(src_path=src_path),
        meta={
            "title": title,
            "date": date,
            "description": f"{title} description",
        },
        title=title,
        url=url,
    )


def test_rss_plugin_writes_multiple_feeds_with_stylesheet(tmp_path):
    plugin = RssPlugin()
    plugin.load_config(
        options={
            "feeds": [
                {"file": "rss.xml", "title": "All pages"},
                {"file": "blog/rss.xml", "title": "Blog", "directories": ["blog"]},
            ]
        }
    )
    config = SimpleNamespace(
        site_dir=tmp_path,
        site_name="Docs",
        site_description="Docs description",
        site_url="https://example.com/docs",
    )

    plugin.on_config(config=config)
    plugin.on_page_markdown(
        markdown="# Blog",
        page=_page(src_path="blog/post.md", url="blog/post/", title="Blog post", date="2025-02-03"),
        config=config,
        files=SimpleNamespace(),
    )
    plugin.on_page_markdown(
        markdown="# Guide",
        page=_page(src_path="guide/page.md", url="guide/page/", title="Guide page", date="2025-01-02"),
        config=config,
        files=SimpleNamespace(),
    )

    plugin.on_post_build(config=config)

    all_feed = (tmp_path / "rss.xml").read_text(encoding="utf-8")
    blog_feed = (tmp_path / "blog/rss.xml").read_text(encoding="utf-8")

    assert (tmp_path / "rss.xsl").exists()
    assert '<?xml-stylesheet type="text/xsl" href="rss.xsl"?>' in all_feed
    assert '<?xml-stylesheet type="text/xsl" href="../rss.xsl"?>' in blog_feed
    assert "<title>Blog post</title>" in all_feed
    assert "<title>Guide page</title>" in all_feed
    assert "<title>Blog post</title>" in blog_feed
    assert "<title>Guide page</title>" not in blog_feed
    assert "<link>https://example.com/docs/blog/post/</link>" in blog_feed
