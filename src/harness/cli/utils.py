import yaml
from jsonpatch import JsonPatch
from json_merge_patch import merge


def load_config(config_content, merge_content=None, patch_content=None):
    config_data = yaml.safe_load(config_content)
    if config_data is None:
        config_data = {}
    if not isinstance(config_data, dict):
        raise SystemExit(f'Invalid configuration format: {type(config_data)!r}')

    if merge_content is not None:
        merge_data = yaml.safe_load(merge_content)
        config_data = merge(config_data, merge_data)

    if patch_content is not None:
        patch_data = yaml.safe_load(patch_content)
        json_patch = JsonPatch(patch_data)
        config_data = json_patch.apply(config_data)
    return config_data
