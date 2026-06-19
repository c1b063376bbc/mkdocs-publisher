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
import re
from typing import Optional

from mkdocs_publisher._shared import markdown_blocks
from mkdocs_publisher.obsidian.config import _ObsidianCalloutsConfig

log = logging.getLogger("mkdocs.publisher.obsidian.callouts")

CALLOUT_BLOCK = re.compile(r"^ *(( ?>)+) *\[!([^]]*)]([\-+]?) *(.*)?")
CALLOUT_BLOCK_FOLLOW = re.compile(r"^ *(( ?>)+) *(.*)?")

CALLOUT_MAPPING = {
    "abstract": ["abstract", "summary", "tldr"],
    "bug": ["bug"],
    "example": ["example"],
    "danger": ["danger", "error"],
    "failure": ["fail", "failure", "missing"],
    "info": ["info"],
    "note": ["note"],
    "question": ["faq", "help", "question"],
    "quote": ["cite", "quote"],
    "tip": ["hint", "important", "tip"],
    "todo": ["todo"],
    "success": ["check", "done", "success"],
    "warning": ["attention", "caution", "warning"],
    "settings": ["settings"],
    "yaml": ["yaml"],
    "none": ["none"],
}
ADMONITION_MAPPING = {callout: admonition for admonition, callouts in CALLOUT_MAPPING.items() for callout in callouts}
INDENTATION_MAPPING = {
    "tabs": "\t",
    "spaces": "    ",
}
FOLDABILITY_MAPPING = {
    "": "!!!",
    "-": "???",
    "+": "???+",
}
ALIGN_MAPPING = {"left": " inline", "right": " inline end"}


class CalloutToAdmonition:
    def __init__(self, callouts_config: _ObsidianCalloutsConfig):
        self._callouts_config: _ObsidianCalloutsConfig = callouts_config
        self._current_file_path: Optional[str] = None

    @staticmethod
    def _callout_indentation(match: re.Match, match_group: int, text_indentation: str = "spaces") -> str:
        initial_indentation = "".join(" " for _ in range(match.start(match_group)))
        indentation = "".join(
            INDENTATION_MAPPING.get(text_indentation, "spaces") for _ in range(match.group(match_group).count(">") - 1)
        )
        return f"{initial_indentation}{indentation}"

    def _callout_block_follow(self, match: re.Match, text_indentation: str = "spaces") -> str:
        indentation = self._callout_indentation(match=match, match_group=1, text_indentation=text_indentation)
        return f"    {indentation} {match.group(3)}"

    @staticmethod
    def _callout_fenced_code_content(match: re.Match, quote_depth: int) -> str:
        literal_quote_depth = max(match.group(1).count(">") - quote_depth, 0)
        literal_quote_prefix = "".join("> " for _ in range(literal_quote_depth))
        return f"{literal_quote_prefix}{match.group(3) or ''}"

    def _callout_fenced_code_block_follow(
        self,
        match: re.Match,
        quote_depth: int,
        text_indentation: str = "spaces",
    ) -> str:
        initial_indentation = "".join(" " for _ in range(match.start(1)))
        indentation = "".join(
            INDENTATION_MAPPING.get(text_indentation, "spaces") for _ in range(max(quote_depth - 1, 0))
        )
        code_content = self._callout_fenced_code_content(match=match, quote_depth=quote_depth)
        return f"    {initial_indentation}{indentation} {code_content}"

    def _callout_block(self, match: re.Match, text_indentation: str = "spaces") -> str:
        # TODO: add possibility to inject customized callout/admonition from CSS/config

        indentation = self._callout_indentation(match=match, match_group=1, text_indentation=text_indentation)

        callout_type = match.group(3).lower()
        if "|" in callout_type:
            callout_type, align = callout_type.split("|")
            align = ALIGN_MAPPING.get(align)
            if align is None:
                log.warning(
                    f'Wrong alignment type "{align}" in file: {self._current_file_path} '
                    f"(fallback to no alignment, possible values {ALIGN_MAPPING.keys()})"
                )
                align = ""
        else:
            align = ""

        admonition_type = ADMONITION_MAPPING.get(callout_type)
        if admonition_type is None:
            log.warning(
                f'There is no callout mapping for "{match.group(3)}" '
                f'in file: {self._current_file_path} (fallback to "note")'
            )
            admonition_type = "note"

        foldable = FOLDABILITY_MAPPING.get(match.group(4))
        if foldable is None:
            log.warning(
                f'Wrong definition of foldable "{match.group(4)}" '
                f"in file: {self._current_file_path} (fallback to non foldable)"
            )
            foldable = "!!!"

        title = match.group(5)
        if title and title not in ['""', "''"]:
            title = f'"{title}"'

        return f"{indentation}{foldable} {admonition_type}{align} {title}"

    def convert_callouts(self, markdown: str, file_path: str) -> str:
        self._current_file_path = file_path
        in_callout_block: bool = False
        outside_fenced_code_block: Optional[markdown_blocks.FencedCodeBlock] = None
        fenced_code_block: Optional[markdown_blocks.FencedCodeBlock] = None
        fenced_code_block_quote_depth: int = 0
        markdown_lines = []
        for line in markdown.split("\n"):
            if not in_callout_block and outside_fenced_code_block is not None:
                markdown_lines.append(line)
                if markdown_blocks.is_fenced_code_block_end(line=line, fenced_code_block=outside_fenced_code_block):
                    outside_fenced_code_block = None
                continue

            callout_match = re.match(CALLOUT_BLOCK, line)
            callout_follow_match = re.match(CALLOUT_BLOCK_FOLLOW, line)

            if not in_callout_block:
                outside_fenced_code_block = markdown_blocks.get_fenced_code_block_start(line=line)
                if outside_fenced_code_block is not None:
                    markdown_lines.append(line)
                    continue

            if in_callout_block and fenced_code_block is not None:
                if callout_follow_match:
                    markdown_lines.append(
                        self._callout_fenced_code_block_follow(
                            match=callout_follow_match,
                            quote_depth=fenced_code_block_quote_depth,
                            text_indentation=self._callouts_config.indentation,
                        )
                    )
                    if markdown_blocks.is_fenced_code_block_end(
                        line=self._callout_fenced_code_content(
                            match=callout_follow_match,
                            quote_depth=fenced_code_block_quote_depth,
                        ),
                        fenced_code_block=fenced_code_block,
                    ):
                        fenced_code_block = None
                        fenced_code_block_quote_depth = 0
                else:
                    in_callout_block = False
                    fenced_code_block = None
                    fenced_code_block_quote_depth = 0
                    markdown_lines.append(line)
            elif callout_match:
                in_callout_block = True
                markdown_lines.append(
                    self._callout_block(match=callout_match, text_indentation=self._callouts_config.indentation)
                )
            elif in_callout_block and callout_follow_match:
                markdown_lines.append(
                    self._callout_block_follow(
                        match=callout_follow_match,
                        text_indentation=self._callouts_config.indentation,
                    )
                )
                fenced_code_block = markdown_blocks.get_fenced_code_block_start(line=callout_follow_match.group(3))
                if fenced_code_block is not None:
                    fenced_code_block_quote_depth = callout_follow_match.group(1).count(">")
            else:
                in_callout_block = False
                fenced_code_block = None
                fenced_code_block_quote_depth = 0
                markdown_lines.append(line)

        return "\n".join(line for line in markdown_lines)
