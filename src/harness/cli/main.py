import argparse


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    from . import kube

    kube.add_commands(subparser)

    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()
