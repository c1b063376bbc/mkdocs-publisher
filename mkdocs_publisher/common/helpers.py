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

from datetime import date
from datetime import datetime
from datetime import time
from typing import Any
from typing import Optional

from mkdocs.config.defaults import MkDocsConfig

from mkdocs_publisher.common.config import CommonConfig
from mkdocs_publisher.common.config import DEFAULT_DATE_FORMAT

COMMON_PLUGIN_NAME = "pub-common"
COMMON_CONFIG_ATTR = "_mkdocs_publisher_common_config"

DEFAULT_TRANSLATIONS = {
    "backlinks_title": "Backlinks",
}

LANGUAGE_TRANSLATIONS = {
    "en": DEFAULT_TRANSLATIONS,
    "pl": {
        "backlinks_title": "Linki zwrotne",
    },
}


def _load_common_config(options: Optional[dict[str, Any]] = None) -> CommonConfig:
    common_config = CommonConfig()
    common_config.load_dict(options or {})
    return common_config


def _plugin_name(plugin: Any) -> Optional[str]:
    if isinstance(plugin, str):
        return plugin
    if isinstance(plugin, dict) and plugin:
        return str(next(iter(plugin.keys())))
    return None


def _raw_plugin_options(plugin: Any) -> dict[str, Any]:
    if isinstance(plugin, dict) and plugin:
        options = next(iter(plugin.values()))
        return options if isinstance(options, dict) else {}
    return {}


def _get_plugin_config(mkdocs_config: MkDocsConfig) -> Any:
    plugins = getattr(mkdocs_config, "plugins", {})
    if isinstance(plugins, list):
        for plugin in plugins:
            if _plugin_name(plugin) == COMMON_PLUGIN_NAME:
                return _raw_plugin_options(plugin)
        return None

    if COMMON_PLUGIN_NAME not in plugins:
        return None

    plugin = plugins[COMMON_PLUGIN_NAME]
    return getattr(plugin, "config", plugin)


def _add_common_plugin_to_raw_config(mkdocs_config: MkDocsConfig) -> None:
    plugins = getattr(mkdocs_config, "plugins", None)
    if not isinstance(plugins, list):
        return
    if any(_plugin_name(plugin) == COMMON_PLUGIN_NAME for plugin in plugins):
        return
    plugins.insert(0, COMMON_PLUGIN_NAME)


def set_common_config(mkdocs_config: MkDocsConfig, common_config: CommonConfig) -> CommonConfig:
    setattr(mkdocs_config, COMMON_CONFIG_ATTR, common_config)
    return common_config


def ensure_common_config(mkdocs_config: MkDocsConfig) -> CommonConfig:
    _add_common_plugin_to_raw_config(mkdocs_config=mkdocs_config)
    common_config = getattr(mkdocs_config, COMMON_CONFIG_ATTR, None)
    if isinstance(common_config, CommonConfig):
        return common_config

    plugin_config = _get_plugin_config(mkdocs_config=mkdocs_config)
    if isinstance(plugin_config, CommonConfig):
        return set_common_config(mkdocs_config=mkdocs_config, common_config=plugin_config)
    if isinstance(plugin_config, dict):
        return set_common_config(mkdocs_config=mkdocs_config, common_config=_load_common_config(plugin_config))

    return set_common_config(mkdocs_config=mkdocs_config, common_config=_load_common_config())


def as_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            try:
                return datetime.strptime(value, DEFAULT_DATE_FORMAT)
            except ValueError:
                return None
    return None


def format_date(value: Any, mkdocs_config: MkDocsConfig) -> Optional[str]:
    date_value = as_datetime(value=value)
    if date_value is None:
        return None
    common_config = ensure_common_config(mkdocs_config=mkdocs_config)
    return date_value.strftime(str(common_config.date_format))


def get_translations(mkdocs_config: MkDocsConfig) -> dict[str, str]:
    common_config = ensure_common_config(mkdocs_config=mkdocs_config)
    translations = dict(DEFAULT_TRANSLATIONS)
    translations.update(LANGUAGE_TRANSLATIONS.get(str(common_config.language), {}))
    translations.update(common_config.translations)
    return translations


def get_translation(mkdocs_config: MkDocsConfig, key: str, default: str) -> str:
    return str(get_translations(mkdocs_config=mkdocs_config).get(key, default))
