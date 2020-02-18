import sys
import argparse


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    from . import kube, check

    kube.add_commands(subparser)
    check.add_commands(subparser)

    args = parser.parse_args()
    if 'func' in args:
        sys.exit(args.func(args) or 0)
    else:
        parser.print_help()
