import hashlib
import tempfile
from enum import Enum
from typing import List, Optional
from base64 import b64encode
from pathlib import Path
from argparse import FileType
from itertools import chain
from contextlib import ExitStack, closing
from dataclasses import dataclass, fields

import yaml
import pkg_resources
from grpc_tools import protoc
from google.protobuf.json_format import ParseDict
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.message_factory import GetMessages

from ..wire_pb2 import HarnessService, HarnessWire

from .utils import load_config


class Protocol(Enum):
    TCP = HarnessWire.TCP
    HTTP = HarnessWire.HTTP
    GRPC = HarnessWire.GRPC

    def k8s_name(self):
        return 'TCP'

    def istio_name(self, suffix):
        return self.name.lower() + '-' + suffix

    def istio_type(self):
        return self.name


class Visibility(Enum):
    PRIVATE = HarnessWire.PRIVATE
    HEADLESS = HarnessWire.HEADLESS
    INTERNAL = HarnessWire.INTERNAL
    PUBLIC = HarnessWire.PUBLIC


class Accessibility(Enum):
    LOCAL = HarnessWire.LOCAL
    NAMESPACE = HarnessWire.NAMESPACE
    CLUSTER = HarnessWire.CLUSTER
    EXTERNAL = HarnessWire.EXTERNAL


@dataclass
class Wire:
    name: str
    type: str
    visibility: Visibility
    protocol: Protocol
    access: Accessibility


@dataclass
class Resource:
    cpu: str
    memory: str


@dataclass
class ConfigurationInfo:
    name: str
    repository: str
    inputs: List[Wire]
    outputs: List[Wire]
    requests: Optional[Resource]
    limits: Optional[Resource]


@dataclass
class Context(ConfigurationInfo):
    config: dict
    version: str

    config_content: str
    config_version: str
    config_volume = 'config'

    secret_merge_content: str
    secret_merge_version: str
    secret_merge_volume = 'config-merge'

    secret_patch_content: str
    secret_patch_version: str
    secret_patch_volume = 'config-patch'

    instance: Optional[str]
    namespace: str
    base_domain: Optional[str]

    @property
    def config_name(self):
        return f'config-{self.config_version}'

    @property
    def secret_merge_name(self):
        return f'config-merge-{self.secret_merge_version}'

    @property
    def secret_patch_name(self):
        return f'config-patch-{self.secret_patch_version}'

    def full_name(self, *parts: str):
        if self.instance is None:
            name = self.name
        else:
            name = f'{self.name}-{self.instance}'
        return '-'.join((name,) + parts)

    def labels(self):
        labels = {'app.kubernetes.io/name': self.name}
        if self.instance is not None:
            labels['app.kubernetes.io/instance'] = self.instance
        return labels

    @property
    def public_domain(self):
        if self.base_domain is not None:
            if self.instance is None:
                return f'{self.name}.{self.base_domain}'
            else:
                return f'{self.name}-{self.instance}.{self.base_domain}'

    def wire_port_num(self, wire: Wire):
        return getattr(self.config, wire.name).bind.port


def gen_deployments(ctx: 'Context'):
    labels = ctx.labels()
    labels['app.kubernetes.io/version'] = ctx.version

    command = [
        'harness',
        'run',
        'svc',
        '/etc/config/config.yaml',
    ]
    if ctx.secret_merge_content is not None:
        command.extend(['--merge', '/etc/config-merge/config.yaml'])
    if ctx.secret_patch_content is not None:
        command.extend(['--patch', '/etc/config-patch/config.yaml'])

    container = dict(
        name='app',
        image=f'{ctx.repository}:{ctx.version}',
        command=command,
        securityContext=dict(
            runAsNonRoot=True,
        ),
        volumeMounts=[
            dict(
                mountPath='/etc/config',
                name=ctx.config_volume,
            ),
        ],
    )
    if ctx.secret_merge_content is not None:
        container['volumeMounts'].append(dict(
            mountPath='/etc/config-merge',
            name=ctx.secret_merge_volume,
        ))
    if ctx.secret_patch_content is not None:
        container['volumeMounts'].append(dict(
            mountPath='/etc/config-patch',
            name=ctx.secret_patch_volume,
        ))

    if ctx.outputs:
        container_ports = container['ports'] = []
        for wire in ctx.outputs:
            container_port = dict(
                name=wire.protocol.istio_name(wire.name),
                containerPort=ctx.wire_port_num(wire),
            )
            protocol = wire.protocol.k8s_name()
            if protocol != 'TCP':
                container_port['protocol'] = protocol
            container_ports.append(container_port)

    for wire in ctx.outputs:
        if wire.visibility not in {Visibility.PUBLIC, Visibility.INTERNAL}:
            continue
        if wire.protocol is Protocol.HTTP:
            container['readinessProbe'] = dict(
                httpGet=dict(
                    path='/health/ready',
                    port=wire.protocol.istio_name(wire.name),
                ),
            )
            container['livenessProbe'] = dict(
                httpGet=dict(
                    path='/health/live',
                    port=wire.protocol.istio_name(wire.name),
                ),
            )
        elif wire.protocol is Protocol.GRPC:
            container['readinessProbe'] = dict(
                exec=dict(
                    command=[
                        'grpc_health_probe',
                        '-addr',
                        f'localhost:{ctx.wire_port_num(wire)}',
                    ],
                ),
            )

    for wire in ctx.inputs:
        if wire.type in {'.harness.logging.Syslog'}:
            pass  # TODO: mount /dev/log volume

    if ctx.requests is not None:
        requests_dict = container.setdefault('resources', {})['requests'] = {}
        if ctx.requests.cpu is not None:
            requests_dict['cpu'] = ctx.requests.cpu
        if ctx.requests.memory is not None:
            requests_dict['memory'] = ctx.requests.memory

    if ctx.limits is not None:
        limits_dict = container.setdefault('resources', {})['limits'] = {}
        if ctx.limits.cpu is not None:
            limits_dict['cpu'] = ctx.limits.cpu
        if ctx.limits.memory is not None:
            limits_dict['memory'] = ctx.limits.memory

    volumes = [
        dict(
            name=ctx.config_volume,
            configMap=dict(
                name=ctx.config_name,
            ),
        ),
    ]
    if ctx.secret_merge_content is not None:
        volumes.append(dict(
            name=ctx.secret_merge_volume,
            secret=dict(
                name=ctx.secret_merge_name,
            ),
        ))
    if ctx.secret_patch_content is not None:
        volumes.append(dict(
            name=ctx.secret_patch_volume,
            secret=dict(
                name=ctx.secret_patch_name,
            ),
        ))

    yield dict(
        apiVersion='apps/v1',
        kind='Deployment',
        metadata=dict(
            name=ctx.full_name(),
            namespace=ctx.namespace,
        ),
        spec=dict(
            selector=dict(
                matchLabels=labels,
            ),
            template=dict(
                metadata=dict(
                    labels=labels,
                ),
                spec=dict(
                    containers=[container],
                ),
            ),
            volumes=volumes,
        ),
    )


def gen_services(ctx: 'Context'):
    def _k8s_svc_port(wire: Wire):
        k8s_port = dict(
            name=wire.protocol.istio_name(wire.name),
            port=ctx.wire_port_num(wire),
            targetPort=wire.protocol.istio_name(wire.name),
        )
        protocol = wire.protocol.k8s_name()
        if protocol != 'TCP':
            k8s_port['protocol'] = protocol
        return k8s_port

    regular_wires = [
        p for p in ctx.outputs
        if p.visibility in {Visibility.INTERNAL, Visibility.PUBLIC}
    ]
    headless_wires = [
        p for p in ctx.outputs if p.visibility is Visibility.HEADLESS
    ]

    if regular_wires:
        yield dict(
            apiVersion='v1',
            kind='Service',
            metadata=dict(
                name=ctx.full_name(),
                namespace=ctx.namespace,
            ),
            spec=dict(
                ports=[_k8s_svc_port(w) for w in regular_wires],
                selector=ctx.labels(),
            ),
        )
    if headless_wires:
        yield dict(
            apiVersion='v1',
            kind='Service',
            metadata=dict(
                name=ctx.full_name('headless'),
                namespace=ctx.namespace,
            ),
            spec=dict(
                clusterIP='None',
                ports=[_k8s_svc_port(w) for w in headless_wires],
                selector=ctx.labels(),
            ),
        )


def gen_virtualservices(ctx: 'Context'):
    internal_wires = [w for w in ctx.outputs if w.visibility is Visibility.INTERNAL]
    public_wires = [w for w in ctx.outputs if w.visibility is Visibility.PUBLIC]
    if not internal_wires and not public_wires:
        return

    hosts = []
    if internal_wires:
        hosts.append(ctx.full_name())
    if public_wires and ctx.public_domain:
        hosts.append(ctx.public_domain)

    if public_wires:
        gateways_mixin = dict(
            gateways=[ctx.full_name(), 'mesh'],
        )
    else:
        gateways_mixin = dict()

    yield dict(
        apiVersion='networking.istio.io/v1alpha3',
        kind='VirtualService',
        metadata=dict(
            name=ctx.full_name(),
            namespace=ctx.namespace,
        ),
        spec=dict(
            hosts=hosts,
            http=[
                dict(
                    match=[dict(port=ctx.wire_port_num(wire))],
                    route=[
                        dict(
                            destination=dict(
                                host=ctx.full_name(),
                                port=dict(number=ctx.wire_port_num(wire)),
                            )
                        )
                    ],
                )
                for wire in chain(public_wires, internal_wires)
            ],
            **gateways_mixin,
        ),
    )


def gen_gateways(ctx: 'Context'):
    outputs = [w for w in ctx.outputs if w.visibility is Visibility.PUBLIC]
    if not outputs or not ctx.public_domain:
        return
    yield dict(
        apiVersion='networking.istio.io/v1alpha3',
        kind='Gateway',
        metadata=dict(
            name=ctx.full_name(),
            namespace=ctx.namespace,
        ),
        spec=dict(
            selector={'istio': 'ingressgateway'},
            servers=[
                dict(
                    port=dict(
                        number=ctx.wire_port_num(wire),
                        protocol=wire.protocol.istio_type(),
                    ),
                    hosts=[ctx.public_domain],
                )
                for wire in outputs
            ],
        ),
    )


def gen_sidecars(ctx: 'Context'):
    hosts = ['istio-system/*']
    for wire in ctx.inputs:
        if wire.access is Accessibility.NAMESPACE:
            assert ctx.namespace
            host = getattr(ctx.config, wire.name).address.host
            hosts.append(f'./{host}.{ctx.namespace}.svc.cluster.local')
        elif wire.access is Accessibility.CLUSTER:
            host = getattr(ctx.config, wire.name).address.host
            hosts.append(f'*/{host}')
        elif wire.access is Accessibility.EXTERNAL:
            host = getattr(ctx.config, wire.name).address.host
            hosts.append(f'./{host}')
        else:
            continue
    yield dict(
        apiVersion='networking.istio.io/v1alpha3',
        kind='Sidecar',
        metadata=dict(
            name=ctx.full_name(),
            namespace=ctx.namespace,
        ),
        spec=dict(
            egress=[dict(
                hosts=hosts,
            )],
            workloadSelector=dict(
                labels=ctx.labels(),
            ),
        ),
    )


def gen_serviceentries(ctx: 'Context'):
    for wire in ctx.inputs:
        if wire.access is not Accessibility.EXTERNAL:
            continue
        yield dict(
            apiVersion='networking.istio.io/v1alpha3',
            kind='ServiceEntry',
            metadata=dict(
                name=ctx.full_name(wire.name),
                namespace=ctx.namespace,
            ),
            spec=dict(
                hosts=[getattr(ctx.config, wire.name).address.host],
                location='MESH_EXTERNAL',
                ports=[dict(
                    number=getattr(ctx.config, wire.name).address.port,
                    protocol=wire.protocol.istio_type(),
                )],
            ),
        )


def gen_configmaps(ctx: 'Context'):
    yield dict(
        apiVersion='v1',
        kind='ConfigMap',
        metadata=dict(
            name=ctx.config_name,
            namespace=ctx.namespace,
        ),
        data={
            'config.yaml': ctx.config_content,
        },
    )


def gen_secrets(ctx: 'Context'):
    def b64(string):
        return b64encode(string.encode('utf-8')).decode('ascii')
    if ctx.secret_merge_content is not None:
        yield dict(
            apiVersion='v1',
            kind='Secret',
            type='Opaque',
            metadata=dict(
                name=ctx.secret_merge_name,
                namespace=ctx.namespace,
            ),
            data={
                'config.yaml': b64(ctx.secret_merge_content),
            },
        )
    if ctx.secret_patch_content is not None:
        yield dict(
            apiVersion='v1',
            kind='Secret',
            type='Opaque',
            metadata=dict(
                name=ctx.secret_patch_name,
                namespace=ctx.namespace,
            ),
            data={
                'config.yaml': b64(ctx.secret_patch_content),
            },
        )


def load(proto_file, proto_path=None):
    wkt_protos = pkg_resources.resource_filename('grpc_tools', '_proto')
    harness_protos = str(Path(__file__).parent.parent.parent.absolute())
    with tempfile.NamedTemporaryFile() as f:
        args = [
            'grpc_tools.protoc',
            '--include_imports',
            f'--proto_path={wkt_protos}',
            f'--proto_path={harness_protos}',
            f'--proto_path={Path(proto_file).parent}',
            f'--descriptor_set_out={f.name}',
        ]
        if proto_path:
            args.extend(f'--proto_path={p}' for p in proto_path)
        args.append(proto_file)
        result = protoc.main(args)
        if result != 0:
            raise Exception('Failed to call protoc')
        content = f.read()
    return FileDescriptorSet.FromString(content)


def get_configuration_info(config_descriptor) -> Optional[ConfigurationInfo]:
    service_name = None
    repository = None
    requests = None
    limits = None

    outputs = []
    inputs = []

    for _, opt in config_descriptor.options.ListFields():
        if isinstance(opt, HarnessService):
            service_name = opt.name
            repository = opt.repository
            if opt.resources is not None:
                if opt.resources.requests is not None:
                    requests = Resource(
                        cpu=opt.resources.requests.cpu or None,
                        memory=opt.resources.requests.memory or None,
                    )
                if opt.resources.limits is not None:
                    limits = Resource(
                        cpu=opt.resources.limits.cpu or None,
                        memory=opt.resources.limits.memory or None,
                    )
    for f in config_descriptor.field:
        for _, opt in f.options.ListFields():
            if isinstance(opt, HarnessWire):
                if opt.WhichOneof('type') == 'input':
                    inputs.append(Wire(
                        f.name,
                        f.type_name,
                        Visibility(opt.visibility),
                        Protocol(opt.protocol),
                        Accessibility(opt.access),
                    ))
                elif opt.WhichOneof('type') == 'output':
                    outputs.append(Wire(
                        f.name,
                        f.type_name,
                        Visibility(opt.visibility),
                        Protocol(opt.protocol),
                        Accessibility(opt.access),
                    ))

    if service_name and repository:
        return ConfigurationInfo(
            service_name,
            repository=repository,
            inputs=inputs,
            outputs=outputs,
            requests=requests,
            limits=limits,
        )
    else:
        return None


def kube_gen(args):
    file_descriptor_set = load(args.proto, args.proto_path)
    with ExitStack() as stack:
        stack.enter_context(closing(args.config))
        config_bytes = args.config.read()
        config_version = hashlib.new('sha1', config_bytes).hexdigest()[:8]
        config_content = config_bytes.decode('utf-8')

        if args.secret_merge is not None:
            stack.enter_context(closing(args.secret_merge))
            secret_merge_bytes = args.secret_merge.read()
            secret_merge_version = hashlib.new('sha1', secret_merge_bytes).hexdigest()[:8]
            secret_merge_content = secret_merge_bytes.decode('utf-8')
        else:
            secret_merge_bytes = None
            secret_merge_version = None
            secret_merge_content = None

        if args.secret_patch is not None:
            stack.enter_context(closing(args.secret_patch))
            secret_patch_bytes = args.secret_patch.read()
            secret_patch_version = hashlib.new('sha1', secret_patch_bytes).hexdigest()[:8]
            secret_patch_content = secret_patch_bytes.decode('utf-8')
        else:
            secret_patch_bytes = None
            secret_patch_version = None
            secret_patch_content = None

    config_data = load_config(
        config_bytes, secret_merge_bytes, secret_patch_bytes,
    )

    file_descriptor, = (f for f in file_descriptor_set.file
                        if args.proto.endswith(f.name))
    for message_type in file_descriptor.message_type:
        if message_type.name == 'Configuration':
            configuration_descriptor = message_type
            break
    else:
        raise Exception(f'Configuration message not found in the {args.proto}')

    message_classes = GetMessages(file_descriptor_set.file)

    config_full_name = '.'.join(filter(None, (
        file_descriptor.package,
        configuration_descriptor.name,
    )))
    config_cls = message_classes[config_full_name]
    config = config_cls()
    ParseDict(config_data, config)
    # TODO: validate config

    config_info = get_configuration_info(configuration_descriptor)
    ctx = Context(
        config=config,
        version=args.version,
        config_content=config_content,
        config_version=config_version,
        secret_merge_content=secret_merge_content,
        secret_merge_version=secret_merge_version,
        secret_patch_content=secret_patch_content,
        secret_patch_version=secret_patch_version,
        instance=args.instance,
        namespace=args.namespace,
        base_domain=args.base_domain,
        **{f.name: getattr(config_info, f.name) for f in fields(config_info)}
    )
    resources = list(chain(
        gen_configmaps(ctx),
        gen_secrets(ctx),
        gen_deployments(ctx),
        gen_services(ctx),
        gen_gateways(ctx),
        gen_virtualservices(ctx),
        gen_serviceentries(ctx),
        gen_sidecars(ctx),
    ))
    print(yaml.dump_all(resources))


def add_commands(subparsers):
    kube_gen_parser = subparsers.add_parser('kube-gen')
    kube_gen_parser.add_argument('-I', '--proto-path', action='append')
    kube_gen_parser.add_argument('proto')
    kube_gen_parser.add_argument('config', type=FileType('rb'))
    kube_gen_parser.add_argument('version')
    kube_gen_parser.add_argument('--instance', default=None)
    kube_gen_parser.add_argument('--namespace', default='default')
    kube_gen_parser.add_argument('--secret-merge', type=FileType('rb'),
                                 default=None)
    kube_gen_parser.add_argument('--secret-patch', type=FileType('rb'),
                                 default=None)
    kube_gen_parser.add_argument('--base-domain', default=None)
    kube_gen_parser.set_defaults(func=kube_gen)
