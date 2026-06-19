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

from mkdocs_publisher.obsidian.callouts import CalloutToAdmonition
from mkdocs_publisher.obsidian.plugin import ObsidianPlugin


def test_convert_callouts_preserves_fenced_code_blocks(pub_obsidian_plugin: ObsidianPlugin):
    markdown = "> [!note] Example\n> ```markdown\n> > [!warning] Not a callout\n> ```"

    callout_to_admonition = CalloutToAdmonition(callouts_config=pub_obsidian_plugin.config.callouts)
    markdown = callout_to_admonition.convert_callouts(markdown=markdown, file_path="main.md")

    assert (
        '!!! note "Example"\n'
        "     ```markdown\n"
        "     > [!warning] Not a callout\n"
        "     ```"
    ) == markdown


def test_convert_callouts_skips_fenced_code_blocks(pub_obsidian_plugin: ObsidianPlugin):
    markdown = "```markdown\n> [!warning] Not a callout\n```\n> [!note] Callout"

    callout_to_admonition = CalloutToAdmonition(callouts_config=pub_obsidian_plugin.config.callouts)
    markdown = callout_to_admonition.convert_callouts(markdown=markdown, file_path="main.md")

    assert "```markdown\n> [!warning] Not a callout\n```\n!!! note \"Callout\"" == markdown
