import hashlib
import tempfile
from enum import Enum
from typing import List, Optional
from base64 import b64encode
from pathlib import Path
from argparse import FileType
from itertools import chain
from dataclasses import dataclass

import yaml
import pkg_resources
from grpc_tools import protoc
from google.protobuf.descriptor_pb2 import FileDescriptorSet

from ..wire_pb2 import HarnessService, HarnessWire


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
class Context:
    name: str
    config: dict
    version: str
    config_content: str
    secret_content: str
    config_version: str
    secret_version: str
    namespace: str
    instance: Optional[str]
    repository: str
    inputs: List[Wire]
    outputs: List[Wire]
    requests: Optional[Resource] = None
    limits: Optional[Resource] = None
    base_domain: Optional[str] = None

    config_vol_name = 'config'
    secret_vol_name = 'secret'

    @property
    def config_name(self):
        return f'config-{self.config_version}'

    @property
    def secret_name(self):
        return f'secret-{self.secret_version}'

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
        return self.config[wire.name]['bind']['port']


def gen_deployments(ctx: 'Context'):
    labels = ctx.labels()
    labels['app.kubernetes.io/version'] = ctx.version

    container = dict(
        name='app',
        image=f'{ctx.repository}:{ctx.version}',
        command=[
            'harness',
            'run',
            'svc',
            '/etc/config/config.yaml',
            '--merge',
            '/etc/secret/config.yaml',
        ],
        securityContext=dict(
            runAsNonRoot=True,
        ),
        volumeMounts=[
            dict(
                mountPath='/etc/config',
                name=ctx.config_vol_name,
            ),
            dict(
                mountPath='/etc/secret',
                name=ctx.secret_vol_name,
            ),
        ],
    )
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
            volumes=[
                dict(
                    name=ctx.config_vol_name,
                    configMap=dict(
                        name=ctx.config_name,
                    ),
                ),
                dict(
                    name=ctx.secret_vol_name,
                    secret=dict(
                        name=ctx.secret_name,
                    ),
                ),
            ],
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
            host = ctx.config[wire.name]['address']['host']
            hosts.append(f'./{host}.{ctx.namespace}.svc.cluster.local')
        elif wire.access is Accessibility.CLUSTER:
            host = ctx.config[wire.name]['address']['host']
            hosts.append(f'*/{host}')
        elif wire.access is Accessibility.EXTERNAL:
            host = ctx.config[wire.name]['address']['host']
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
                hosts=[ctx.config[wire.name]['address']['host']],
                location='MESH_EXTERNAL',
                ports=[dict(
                    number=ctx.config[wire.name]['address']['port'],
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
    yield dict(
        apiVersion='v1',
        kind='Secret',
        type='Opaque',
        metadata=dict(
            name=ctx.secret_name,
            namespace=ctx.namespace,
        ),
        data={
            'config.yaml': (
                b64encode(ctx.secret_content.encode('utf-8')).decode('utf-8')
            ),
        },
    )


def load(proto_file, proto_path=None):
    wkt_protos = pkg_resources.resource_filename('grpc_tools', '_proto')
    harness_protos = str(Path(__file__).parent.parent.parent.absolute())
    with tempfile.NamedTemporaryFile() as f:
        args = [
            'grpc_tools.protoc',
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
    return FileDescriptorSet.FromString(content).file[0]


def create_context(
    file_descriptor,
    *,
    config,
    version,
    config_content,
    secret_content,
    config_version,
    secret_version,
    namespace,
    base_domain=None,
    instance=None,
):
    service_name = None
    repository = None
    requests = None
    limits = None

    outputs = []
    inputs = []

    for mt in file_descriptor.message_type:
        for _, opt in mt.options.ListFields():
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
        for f in mt.field:
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
        return Context(
            service_name,
            config,
            version=version,
            config_content=config_content,
            secret_content=secret_content,
            config_version=config_version,
            secret_version=secret_version,
            namespace=namespace,
            instance=instance,
            repository=repository,
            inputs=inputs,
            outputs=outputs,
            requests=requests,
            limits=limits,
            base_domain=base_domain,
        )
    else:
        return None


def kube_gen(args):
    file_descriptor = load(args.proto, args.proto_path)
    with args.config:
        config_content = args.config.read()
    with args.secret:
        secret_content = args.secret.read()

    config_data = yaml.safe_load(config_content)
    config_version = (
        hashlib.new('sha1', config_content.encode('utf-8'))
        .hexdigest()[:8]
    )
    secret_version = (
        hashlib.new('sha1', secret_content.encode('utf-8'))
        .hexdigest()[:8]
    )

    ctx = create_context(
        file_descriptor,
        config=config_data,
        version=args.version,
        config_content=config_content,
        secret_content=secret_content,
        config_version=config_version,
        secret_version=secret_version,
        base_domain=args.base_domain,
        namespace=args.namespace,
        instance=args.instance,
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
    kube_gen_parser.add_argument('proto')
    kube_gen_parser.add_argument('config', type=FileType(encoding='utf-8'))
    kube_gen_parser.add_argument('secret', type=FileType(encoding='utf-8'))
    kube_gen_parser.add_argument('version')
    kube_gen_parser.add_argument('-I', '--proto-path', action='append')
    kube_gen_parser.add_argument('--namespace', default='default')
    kube_gen_parser.add_argument('--instance', default=None)
    kube_gen_parser.add_argument('--base-domain', default=None)
    kube_gen_parser.set_defaults(func=kube_gen)
