import faker
import pytest

from harness.cli.kube import gen_configmaps, Context
from harness.wire_pb2 import HarnessService


f = faker.Faker()


def get_context(**kwargs):
    params = dict(
        _container=HarnessService.Container(),
        name=f.pystr(),
        inputs=[],
        outputs=[],
        host_paths=[],
        entrypoint=[f.pystr(), f.pystr()],
        config_content=f.pystr(),
        config_hash=f.pystr(),
        secret_merge_content=None,
        secret_merge_hash=None,
        secret_patch_content=None,
        secret_patch_hash=None,
        version=f.pystr(),
        instance=None,
        namespace=f.pystr(),
        base_domain=None,
    )
    params.update(kwargs)
    return Context(**params)


@pytest.mark.parametrize('instance', [None, 'org'])
def test_gen_configmaps(instance):
    ctx = get_context(
        name='foo',
        namespace='bar',
        instance=instance,
        config_content='<content>',
        config_hash='beef',
    )
    assert list(gen_configmaps(ctx)) == [
        dict(
            apiVersion='v1',
            kind='ConfigMap',
            metadata=dict(
                name=(
                    'foo-org-config-beef' if instance
                    else 'foo-config-beef'
                ),
                namespace='bar',
            ),
            data={
                'config.yaml': '<content>',
            },
        )
    ]
