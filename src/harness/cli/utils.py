import yaml
from jsonpatch import JsonPatch
from json_merge_patch import merge


def load_config(config_bytes, merge_bytes=None, patch_bytes=None):
    config_data = yaml.safe_load(config_bytes.decode('utf-8'))
    if config_data is None:
        config_data = {}
    if not isinstance(config_data, dict):
        raise SystemExit(f'Invalid configuration format: {type(config_data)!r}')

    if merge_bytes is not None:
        merge_data = yaml.safe_load(merge_bytes.decode('utf-8'))
        config_data = merge(config_data, merge_data)

    if patch_bytes is not None:
        patch_data = yaml.safe_load(patch_bytes.decode('utf-8'))
        json_patch = JsonPatch(patch_data)
        config_data = json_patch.apply(config_data)
    return config_data
