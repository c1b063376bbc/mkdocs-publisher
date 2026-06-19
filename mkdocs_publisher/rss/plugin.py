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

import logging
import os
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any
from typing import Optional
from urllib.parse import urljoin
from xml.etree import ElementTree

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import event_priority
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from mkdocs_publisher.rss.config import RssConfig

log = logging.getLogger("mkdocs.publisher.rss.plugin")

DEFAULT_FEED: dict[str, Any] = {
    "file": "rss.xml",
    "directories": [],
}
RSS_XSL = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="utf-8" indent="yes"/>
  <xsl:template match="/rss/channel">
    <html>
      <head>
        <title><xsl:value-of select="title"/></title>
        <style>
          body { font: 16px/1.5 sans-serif; margin: 2rem auto; max-width: 48rem; padding: 0 1rem; }
          article { border-top: 1px solid #ddd; padding: 1rem 0; }
          time { color: #666; display: block; font-size: .875rem; }
        </style>
      </head>
      <body>
        <h1><xsl:value-of select="title"/></h1>
        <p><xsl:value-of select="description"/></p>
        <xsl:for-each select="item">
          <article>
            <h2><a href="{link}"><xsl:value-of select="title"/></a></h2>
            <time><xsl:value-of select="pubDate"/></time>
            <p><xsl:value-of select="description"/></p>
          </article>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
"""


@dataclass
class RssItem:
    source_path: str
    title: str
    url: str
    description: str
    published: Optional[datetime]
    updated: Optional[datetime]


class RssPlugin(BasePlugin[RssConfig]):
    def __init__(self):
        self._items: list[RssItem] = []

    @staticmethod
    def _as_datetime(value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            item_datetime = value
        elif isinstance(value, date):
            item_datetime = datetime.combine(value, time.min)
        elif isinstance(value, str):
            try:
                item_datetime = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        else:
            return None

        if item_datetime.tzinfo is None:
            item_datetime = item_datetime.replace(tzinfo=timezone.utc)
        return item_datetime

    @staticmethod
    def _rss_date(value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return format_datetime(value.astimezone(timezone.utc), usegmt=True)

    @staticmethod
    def _matches_directories(source_path: str, directories: list[str]) -> bool:
        if not directories:
            return True

        page_path = Path(source_path)
        for directory in directories:
            directory_path = Path(str(directory))
            if directory in ["", "."] or page_path == directory_path or directory_path in page_path.parents:
                return True
        return False

    @staticmethod
    def _feed_config(feed: dict) -> dict[str, Any]:
        feed_config = DEFAULT_FEED.copy()
        feed_config.update(feed)
        if isinstance(feed_config["directories"], str):
            feed_config["directories"] = [feed_config["directories"]]
        return feed_config

    @staticmethod
    def _stylesheet_href(feed_file: Path, xsl_file: Path) -> str:
        return Path(os.path.relpath(xsl_file, start=feed_file.parent)).as_posix()

    @staticmethod
    def _absolute_url(site_url: str, page_url: str) -> str:
        if not site_url:
            return page_url
        return urljoin(f"{site_url.rstrip('/')}/", page_url.lstrip("/"))

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        self._items = []
        return config

    def on_page_markdown(self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files) -> Optional[str]:
        title = page.meta.get("title", page.title or Path(page.file.src_path).stem)
        self._items.append(
            RssItem(
                source_path=str(page.file.src_path),
                title=str(title),
                url=self._absolute_url(site_url=str(config.site_url or ""), page_url=page.url),
                description=str(page.meta.get(self.config.description_key, "")),
                published=self._as_datetime(page.meta.get(self.config.date_key)),
                updated=self._as_datetime(page.meta.get(self.config.update_key)),
            )
        )
        return markdown

    def _render_feed(self, feed: dict, config: MkDocsConfig, feed_file: Path, xsl_file: Optional[Path]) -> str:
        channel_title = feed.get("title") or config.site_name
        channel_description = feed.get("description") or getattr(config, "site_description", "") or channel_title
        channel_link = str(getattr(config, "site_url", "") or "")

        rss = ElementTree.Element("rss", {"version": "2.0"})
        channel = ElementTree.SubElement(rss, "channel")
        ElementTree.SubElement(channel, "title").text = str(channel_title)
        ElementTree.SubElement(channel, "link").text = channel_link
        ElementTree.SubElement(channel, "description").text = str(channel_description)
        ElementTree.SubElement(channel, "generator").text = "mkdocs-publisher"

        items = [
            item
            for item in self._items
            if self._matches_directories(source_path=item.source_path, directories=feed.get("directories", []))
        ]
        item_dates = [item_date for item in items for item_date in [item.published, item.updated] if item_date]
        last_build_date = self._rss_date(max(item_dates)) if item_dates else None
        if last_build_date is not None:
            ElementTree.SubElement(channel, "lastBuildDate").text = last_build_date

        items.sort(
            key=lambda item: item.published or item.updated or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )

        for item in items:
            rss_item = ElementTree.SubElement(channel, "item")
            ElementTree.SubElement(rss_item, "title").text = item.title
            ElementTree.SubElement(rss_item, "link").text = item.url
            ElementTree.SubElement(rss_item, "guid", {"isPermaLink": "true"}).text = item.url
            ElementTree.SubElement(rss_item, "description").text = item.description

            item_date = self._rss_date(item.published)
            if item_date is not None:
                ElementTree.SubElement(rss_item, "pubDate").text = item_date

        ElementTree.indent(rss, space="  ")
        xml = ElementTree.tostring(rss, encoding="unicode")
        if xsl_file is not None:
            stylesheet_href = self._stylesheet_href(feed_file=feed_file, xsl_file=xsl_file)
            return (
                '<?xml version="1.0" encoding="utf-8"?>\n'
                f'<?xml-stylesheet type="text/xsl" href="{stylesheet_href}"?>\n'
                f"{xml}\n"
            )
        return f'<?xml version="1.0" encoding="utf-8"?>\n{xml}\n'

    @event_priority(-100)
    def on_post_build(self, *, config: MkDocsConfig) -> None:
        site_dir = Path(config.site_dir)
        xsl_file: Optional[Path] = None
        if self.config.xsl_enabled:
            xsl_file = site_dir / self.config.xsl_file
            xsl_file.parent.mkdir(parents=True, exist_ok=True)
            xsl_file.write_text(RSS_XSL, encoding="utf-8")
            log.debug(f"RSS stylesheet written: {xsl_file}")

        for feed in self.config.feeds:
            feed_config = self._feed_config(feed=feed)
            feed_file = site_dir / feed_config["file"]
            feed_file.parent.mkdir(parents=True, exist_ok=True)
            feed_file.write_text(
                self._render_feed(feed=feed_config, config=config, feed_file=feed_file, xsl_file=xsl_file),
                encoding="utf-8",
            )
            log.info(f"RSS feed written: {feed_file}")
