import argparse

from rich.markdown import Markdown

from . import config_loader, daemon, pub
from .paragraph_rich import HelpFormatter

description = """
Send messages and commands between machines.
"""


def setup_args_parser(config):
    parser = argparse.ArgumentParser(
        description=Markdown(description, style="argparse.text"),
        formatter_class=HelpFormatter,
    )
    subparsers = parser.add_subparsers(title="subcommands")
    pub.setup_args_parser(subparsers, config)
    daemon.setup_args_parser(subparsers, config)

    return parser


def main():
    config = config_loader.load()
    parser = setup_args_parser(config)
    args = parser.parse_args()
    if "func" in args:
        # print('yup', args)
        args.func(config, args)
    else:
        parser.print_help()
