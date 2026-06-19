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

import re
from dataclasses import dataclass
from typing import Callable
from typing import Optional

FENCED_CODE_BLOCK_START = re.compile(r"^(?P<prefix>[ \t]{0,3}(?:>[ \t]?)*)(?P<fence>`{3,}|~{3,}).*$")


@dataclass
class FencedCodeBlock:
    char: str
    length: int
    is_quoted: bool


def get_fenced_code_block_start(line: str) -> Optional[FencedCodeBlock]:
    match = re.match(FENCED_CODE_BLOCK_START, line.rstrip("\r\n"))
    if match is None:
        return None

    fence = match.group("fence")
    return FencedCodeBlock(
        char=fence[0],
        length=len(fence),
        is_quoted=">" in match.group("prefix"),
    )


def is_fenced_code_block_end(line: str, fenced_code_block: FencedCodeBlock) -> bool:
    line = line.rstrip("\r\n")
    quote_prefix = r"(?:>[ \t]?)*" if fenced_code_block.is_quoted else ""
    return bool(
        re.match(
            rf"^[ \t]{{0,3}}{quote_prefix}{re.escape(fenced_code_block.char)}"
            rf"{{{fenced_code_block.length},}}[ \t]*$",
            line,
        )
    )


def apply_outside_fenced_code_blocks(markdown: str, callback: Callable[[str], str]) -> str:
    fenced_code_block: Optional[FencedCodeBlock] = None
    markdown_lines = []
    outside_block_lines = []

    def append_outside_block() -> None:
        if outside_block_lines:
            markdown_lines.append(callback("".join(outside_block_lines)))
            outside_block_lines.clear()

    for line in markdown.splitlines(keepends=True):
        if fenced_code_block is not None:
            markdown_lines.append(line)
            if is_fenced_code_block_end(line=line, fenced_code_block=fenced_code_block):
                fenced_code_block = None
            continue

        fenced_code_block = get_fenced_code_block_start(line=line)
        if fenced_code_block is not None:
            append_outside_block()
            markdown_lines.append(line)
        else:
            outside_block_lines.append(line)

    append_outside_block()
    return "".join(markdown_lines)
