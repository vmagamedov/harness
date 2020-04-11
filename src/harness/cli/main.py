import sys
import argparse
from typing import Any


def add_kubegen(subparsers: Any) -> None:
    def func(args: argparse.Namespace) -> None:
        from . import kubegen

        kubegen.kube_gen(
            args.runtime,
            args.proto,
            args.config,
            args.version,
            proto_path=args.proto_path,
            secret_merge=args.secret_merge,
            secret_patch=args.secret_patch,
            instance=args.instance,
            namespace=args.namespace,
            base_domain=args.base_domain,
        )

    parser = subparsers.add_parser("kube-gen")
    parser.add_argument("-I", "--proto-path", action="append")
    parser.add_argument("runtime", choices=("python",))
    parser.add_argument("proto")
    parser.add_argument("config", type=argparse.FileType("rb"))
    parser.add_argument("version")
    parser.add_argument("--instance", default=None)
    parser.add_argument("--namespace", default="default")
    parser.add_argument("--secret-merge", type=argparse.FileType("rb"), default=None)
    parser.add_argument("--secret-patch", type=argparse.FileType("rb"), default=None)
    parser.add_argument("--base-domain", default=None)
    parser.set_defaults(func=func)


def add_check(subparsers: Any) -> None:
    def func(args: argparse.Namespace) -> None:
        from . import check

        check.check(
            args.proto,
            args.config,
            args.proto_path,
            merge_file=args.merge,
            patch_file=args.patch,
        )

    parser = subparsers.add_parser("check")
    parser.add_argument("-I", "--proto-path", action="append")
    parser.add_argument("proto")
    parser.add_argument("config", type=argparse.FileType(encoding="utf-8"))
    parser.add_argument(
        "--merge", type=argparse.FileType(encoding="utf-8"), default=None
    )
    parser.add_argument(
        "--patch", type=argparse.FileType(encoding="utf-8"), default=None
    )
    parser.set_defaults(func=func)


def add_protopath(subparsers: Any) -> None:
    def func(_: argparse.Namespace) -> None:
        from . import protopath

        protopath.proto_path()

    check_parser = subparsers.add_parser("proto-path")
    check_parser.set_defaults(func=func)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    add_kubegen(subparser)
    add_check(subparser)
    add_protopath(subparser)

    args = parser.parse_args()
    if "func" in args:
        sys.exit(args.func(args) or 0)
    else:
        parser.print_help()
