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

from collections import OrderedDict
from datetime import datetime
from types import SimpleNamespace

from mkdocs_publisher.blog import creators
from mkdocs_publisher.blog.structures import BlogConfig
from mkdocs_publisher.blog.structures import BlogPost
from mkdocs_publisher.blog.structures import Translation


def _translation() -> Translation:
    return Translation(
        teaser_link_text="Read more",
        blog_page_title="Blog",
        blog_navigation_name="Blog",
        recent_blog_posts_navigation_name="Recent posts",
        archive_page_title="Archive",
        archive_navigation_name="Archive",
        categories_page_title="Category",
        categories_navigation_name="Categories",
        tags_page_title="Tag",
        tags_navigation_name="Tags",
        newer_posts="Newer posts",
        older_posts="Older posts",
    )


def test_create_blog_post_pages_can_skip_categories_and_tags(tmp_path):
    blog_config = BlogConfig()
    blog_config.temp_dir = tmp_path
    blog_config.site_dir = tmp_path / "site"
    blog_config.temp_files = {}
    blog_config.translation = _translation()
    blog_config.mkdocs_config = SimpleNamespace(site_url="", use_directory_urls=True)
    blog_config.plugin_config = SimpleNamespace(
        blog_dir="blog",
        posts_per_page=5,
        archive_subdir="archive",
        categories_subdir="categories",
        tags_subdir="tags",
        slug="blog",
        searchable_non_posts=False,
        categories_pages_enabled=False,
        tags_pages_enabled=False,
    )
    date = datetime(2025, 1, 1)
    blog_config.blog_posts = {
        date: BlogPost(
            title="Post",
            date=date,
            path="blog/post.md",
            content="Post content",
            tags=["tag"],
            categories=["category"],
            slug="post",
            teaser="Post teaser",
        )
    }
    config_nav = OrderedDict()

    creators.create_blog_post_pages(start_page=False, blog_config=blog_config, config_nav=config_nav)

    blog_nav = config_nav["Blog"]
    assert {"Categories": []} not in blog_nav
    assert {"Tags": []} not in blog_nav
    assert "categories/category" not in blog_config.temp_files
    assert "tags/tag" not in blog_config.temp_files
