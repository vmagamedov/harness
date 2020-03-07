import faker
import pytest

from harness.cli import kubegen
from harness.config import WireSpec
from harness.wire_pb2 import Service, Wire, Output, Mark

f = faker.Faker()


def get_context(**kwargs):
    params = dict(
        _container=Service.Container(),
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
    return kubegen.Context(**params)


@pytest.mark.parametrize('instance', [None, 'org'])
@pytest.mark.parametrize('namespace', [None, 'acme'])
@pytest.mark.parametrize('base_domain', [None, 'example.com'])
def test_smoke(instance, namespace, base_domain):
    ctx = get_context(
        namespace=namespace,
        instance=instance,
        base_domain=base_domain,
    )
    list(kubegen.gen_deployments(ctx))
    list(kubegen.gen_services(ctx))
    list(kubegen.gen_virtualservices(ctx))
    list(kubegen.gen_gateways(ctx))
    list(kubegen.gen_sidecars(ctx))
    list(kubegen.gen_serviceentries(ctx))
    list(kubegen.gen_configmaps(ctx))
    list(kubegen.gen_secrets(ctx))


@pytest.mark.parametrize('instance', [None, 'org'])
def test_gen_configmaps(instance):
    ctx = get_context(
        name='foo',
        namespace='bar',
        instance=instance,
        config_content='<content>',
        config_hash='beef',
    )
    assert list(kubegen.gen_configmaps(ctx)) == [
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


@pytest.mark.parametrize('optional', [True, False])
@pytest.mark.parametrize('empty', [True, False])
def test_get_socket(message_types, config_type, optional, empty):
    """
    import "harness/net.proto";

    message Configuration {
        harness.net.Server server = 1;
    }
    """
    wire = WireSpec(
        name='server',
        type='harness.net.Server',
        value=Wire(output=Output(type='path.to.OutputWire')),
        optional=optional,
    )
    if empty:
        config = config_type()
        if optional:
            assert kubegen.get_socket(wire, message_types, config) is None
        else:
            with pytest.raises(AssertionError, match='Config unset'):
                kubegen.get_socket(wire, message_types, config)
    else:
        config = config_type(
            server=dict(
                bind=dict(
                    host='localhost',
                    port=5000,
                ),
            ),
        )
        socket = kubegen.get_socket(wire, message_types, config)
        assert socket == kubegen.Socket(
            host='localhost',
            port=5000,
            _protocol=Mark.Protocol.TCP,
        )
