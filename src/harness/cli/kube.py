import json
import tempfile
import subprocess


def create_configmap(args):
    get_config_run = subprocess.run(
        f"kubectl create configmap {args.name}"
        f" --dry-run"
        f" --append-hash=true"
        f" --from-file=config.yaml={args.config}"
        f" -o json",
        shell=True,
        check=True,
        capture_output=True,
    )
    config = json.loads(get_config_run.stdout)
    with tempfile.NamedTemporaryFile() as f:
        f.write(get_config_run.stdout)
        f.flush()
        subprocess.run(
            f"kubectl apply -f {f.name}",
            shell=True,
            check=True,
            capture_output=True,
        )
    print(config['metadata']['name'], end='')


def create_secret(args):
    get_secret_run = subprocess.run(
        f"kubectl create secret generic {args.name}"
        f" --dry-run"
        f" --append-hash=true"
        f" --from-file=config.yaml={args.config}"
        f" -o json",
        shell=True,
        check=True,
        capture_output=True,
    )
    secret = json.loads(get_secret_run.stdout)
    with tempfile.NamedTemporaryFile() as f:
        f.write(get_secret_run.stdout)
        f.flush()
        subprocess.run(
            f"kubectl apply -f {f.name}",
            shell=True,
            check=True,
            capture_output=True,
        )
    print(secret['metadata']['name'], end='')


def add_commands(subparsers):
    configmap_parser = subparsers.add_parser('create-configmap')
    configmap_parser.add_argument(
        'name',
    )
    configmap_parser.add_argument(
        'config',
    )
    configmap_parser.set_defaults(func=create_configmap)

    secret_parser = subparsers.add_parser('create-secret')
    secret_parser.add_argument(
        'name',
    )
    secret_parser.add_argument(
        'config',
    )
    secret_parser.set_defaults(func=create_secret)
