import argparse
from rich.containers import Lines
from rich.text import Text

from rich_argparse import RichHelpFormatter
from rich_argparse._common import _rich_wrap


# See https://github.com/hamdanal/rich-argparse/issues/140#issuecomment-2558440424
class ParagraphRichHelpFormatter(RichHelpFormatter):
    """Rich help message formatter which retains paragraph separation."""

    def _rich_split_lines(self, text: Text, width: int) -> Lines:
        lines = Lines()
        for paragraph in text.split("\n\n"):
            cleaned_paragraph = self._rich_whitespace_sub(paragraph)
            paragraph_lines = _rich_wrap(self.console, cleaned_paragraph, width)
            lines.extend(paragraph_lines)
            lines.append(Text("\n"))  # Add a blank line between paragraphs
        if lines:
            lines.pop()  # Remove trailing newline
        return lines

    def _rich_fill_text(self, text: Text, width: int, indent: Text) -> Text:
        lines = self._rich_split_lines(text, width)
        return Text("\n").join(indent + line for line in lines) + "\n"


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, ParagraphRichHelpFormatter):
    pass
