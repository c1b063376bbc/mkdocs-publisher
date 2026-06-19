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

import hashlib
import logging
import os
import re
from pathlib import Path
from typing import Optional
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen

from bs4 import BeautifulSoup
from bs4 import Tag
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import event_priority
from mkdocs.structure.pages import Page

from mkdocs_publisher.offline.config import OfflineConfig

log = logging.getLogger("mkdocs.publisher.offline.plugin")

USER_AGENT = "mkdocs-publisher-offline"


class OfflinePlugin(BasePlugin[OfflineConfig]):
    def __init__(self):
        self._downloaded_assets: dict[str, Path] = {}

    @staticmethod
    def _is_remote_url(url: str) -> bool:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ["http", "https"] or url.startswith("//")

    @staticmethod
    def _normalize_url(url: str) -> str:
        if url.startswith("//"):
            return f"https:{url}"
        return url

    @staticmethod
    def _local_file_name(url: str, default_suffix: str) -> str:
        parsed_url = urlparse(url)
        path = Path(parsed_url.path)
        suffix = path.suffix or default_suffix
        stem = path.stem or "asset"
        stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-") or "asset"
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[0:12]
        return f"{stem}-{url_hash}{suffix}"

    @staticmethod
    def _relative_asset_path(asset_path: Path, page: Page, config: MkDocsConfig) -> str:
        page_dest_uri = Path(page.file.dest_uri)
        page_dest_dir = (Path(config.site_dir) / page_dest_uri).parent
        return Path(os.path.relpath(asset_path, start=page_dest_dir)).as_posix()

    def _download_asset(self, url: str, default_suffix: str, config: MkDocsConfig) -> Optional[Path]:
        url = self._normalize_url(url=url)
        if url in self._downloaded_assets:
            return self._downloaded_assets[url]

        assets_dir = Path(config.site_dir) / self.config.assets_dir
        assets_dir.mkdir(parents=True, exist_ok=True)
        asset_path = assets_dir / self._local_file_name(url=url, default_suffix=default_suffix)

        if asset_path.exists() and not self.config.overwrite:
            self._downloaded_assets[url] = asset_path
            return asset_path

        try:
            request = Request(url=url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=self.config.timeout) as response:
                asset_path.write_bytes(response.read())
        except (OSError, URLError) as err:
            log.warning(f"Cannot download offline asset '{url}': {err}")
            return None

        log.debug(f"Downloaded offline asset: {url} -> {asset_path}")
        self._downloaded_assets[url] = asset_path
        return asset_path

    def _replace_asset_url(
        self,
        tag: Tag,
        attr: str,
        default_suffix: str,
        page: Page,
        config: MkDocsConfig,
    ) -> None:
        url = tag.get(attr)
        if not isinstance(url, str) or not self._is_remote_url(url=url):
            return

        asset_path = self._download_asset(url=url, default_suffix=default_suffix, config=config)
        if asset_path is None:
            return

        tag[attr] = self._relative_asset_path(asset_path=asset_path, page=page, config=config)

    @event_priority(-100)
    def on_post_page(self, output: str, *, page: Page, config: MkDocsConfig) -> Optional[str]:
        soup = BeautifulSoup(markup=output, features="html.parser")

        if self.config.scripts.enabled:
            for tag in soup.find_all("script", src=True):
                self._replace_asset_url(tag=tag, attr="src", default_suffix=".js", page=page, config=config)

        if self.config.stylesheets.enabled:
            for tag in soup.find_all("link", href=True):
                rel = tag.get("rel", [])
                if isinstance(rel, str):
                    rel = [rel]
                if "stylesheet" in rel:
                    self._replace_asset_url(tag=tag, attr="href", default_suffix=".css", page=page, config=config)

        if self.config.images.enabled:
            for tag in soup.find_all("img", src=True):
                self._replace_asset_url(tag=tag, attr="src", default_suffix=".img", page=page, config=config)

        return str(soup)
