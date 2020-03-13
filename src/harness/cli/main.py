import sys
import argparse


def add_kubegen_commands(subparsers):
    def func(args):
        from . import kubegen
        kubegen.kube_gen(args)
    parser = subparsers.add_parser('kube-gen')
    parser.add_argument('-I', '--proto-path', action='append')
    parser.add_argument('runtime', choices=('python',))
    parser.add_argument('proto')
    parser.add_argument('config', type=argparse.FileType('rb'))
    parser.add_argument('version')
    parser.add_argument('--instance', default=None)
    parser.add_argument('--namespace', default='default')
    parser.add_argument('--secret-merge', type=argparse.FileType('rb'),
                        default=None)
    parser.add_argument('--secret-patch', type=argparse.FileType('rb'),
                        default=None)
    parser.add_argument('--base-domain', default=None)
    parser.set_defaults(func=func)


def add_check_commands(subparsers):
    def func(args):
        from . import check
        check.check(args)
    parser = subparsers.add_parser('check')
    parser.add_argument('-I', '--proto-path', action='append')
    parser.add_argument('proto')
    parser.add_argument('config', type=argparse.FileType(encoding='utf-8'))
    parser.add_argument('--merge', type=argparse.FileType(encoding='utf-8'),
                        default=None)
    parser.add_argument('--patch', type=argparse.FileType(encoding='utf-8'),
                        default=None)
    parser.set_defaults(func=func)


def add_protopath_commands(subparsers):
    def func(args):
        from . import protopath
        protopath.proto_path(args)
    check_parser = subparsers.add_parser('proto-path')
    check_parser.set_defaults(func=func)


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    add_kubegen_commands(subparser)
    add_check_commands(subparser)
    add_protopath_commands(subparser)

    args = parser.parse_args()
    if 'func' in args:
        sys.exit(args.func(args) or 0)
    else:
        parser.print_help()
