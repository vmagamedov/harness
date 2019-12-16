import os
import sys
from enum import Enum
from typing import List
from pathlib import Path
from itertools import chain
from dataclasses import dataclass

# from pkg_resources import iter_entry_points, EntryPoint

import yaml

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorResponse


class Protocol(Enum):
    HTTP = 'http'
    GRPC = 'grpc'


class PortType(Enum):
    PRIVATE = 1
    HEADLESS = 2
    INTERNAL = 3
    PUBLIC = 4


@dataclass
class Port:
    protocol: Protocol
    name: str
    number: int
    type: PortType


def _get_full_name(name, singleton=False):
    if singleton:
        return name
    else:
        return f'{name}-{{{{ .Release.Name }}}}'


def _get_labels(name, singleton=False):
    labels = {'app.kubernetes.io/name': name}
    if not singleton:
        labels['app.kubernetes.io/instance'] = '{{ .Release.Name }}'
    return labels


def _k8s_protocol(name):
    return {Protocol.HTTP: 'TCP', Protocol.GRPC: 'TCP'}[name]


def chart(name):
    return dict(
        apiVersion='v1',
        appVersion='1.0',
        name=name,
        version='dev',
    )


def _k8s_container_port(port: Port):
    k8s_port = dict(
        name=port.name,
        containerPort=port.number,
    )
    protocol = _k8s_protocol(port.protocol)
    if protocol != 'TCP':
        k8s_port['protocol'] = protocol
    return k8s_port


def deployments(
    name: str,
    *,
    singleton: bool,
    repository: str,
    ports: List[Port],
):
    labels = _get_labels(name, singleton)
    labels['app.kubernetes.io/version'] = '{{ .Values.version }}'

    if ports:
        ports_mixin = dict(ports=list(map(_k8s_container_port, ports)))
    else:
        ports_mixin = dict()

    yield dict(
        apiVersion='apps/v1',
        kind='Deployment',
        metadata=dict(
            name=_get_full_name(name, singleton),
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
                    containers=[
                        dict(
                            name='app',
                            image=f'{repository}:{{{{ .Values.version }}}}',
                            **ports_mixin,
                        ),
                    ],
                ),
            ),
        ),
    )


def _k8s_svc_port(port: Port):
    k8s_port = dict(
        name=port.name,
        port=port.number,
        targetPort=port.name,
    )
    protocol = _k8s_protocol(port.protocol)
    if protocol != 'TCP':
        k8s_port['protocol'] = protocol
    return k8s_port


def services(
    name: str,
    singleton: bool,
    ports: List[Port],
):
    regular_ports = [
        p for p in ports if p.type in {PortType.INTERNAL, PortType.PUBLIC}
    ]
    headless_ports = [
        p for p in ports if p.type is PortType.HEADLESS
    ]

    if regular_ports:
        yield dict(
            apiVersion='v1',
            kind='Service',
            metadata=dict(
                name=_get_full_name(name, singleton),
            ),
            spec=dict(
                ports=list(map(_k8s_svc_port, regular_ports)),
                selector=_get_labels(name, singleton),
            ),
        )
    if headless_ports:
        yield dict(
            apiVersion='v1',
            kind='Service',
            metadata=dict(
                name=_get_full_name(name, singleton) + '-headless',
            ),
            spec=dict(
                clusterIP='None',
                ports=list(map(_k8s_svc_port, headless_ports)),
                selector=_get_labels(name, singleton),
            ),
        )


def virtual_services(
    name: str,
    *,
    singleton: bool,
    domain: str,
    ports: List[Port],
):
    internal_ports = [p for p in ports if p.type is PortType.INTERNAL]
    public_ports = [p for p in ports if p.type is PortType.PUBLIC]
    if not internal_ports and not public_ports:
        return

    hosts = []
    if internal_ports:
        hosts.append(_get_full_name(name, singleton))
    if public_ports:
        hosts.append(domain)

    if public_ports:
        gateways_mixin = dict(
            gateways=[_get_full_name(name, singleton), 'mesh'],
        )
    else:
        gateways_mixin = dict()

    yield dict(
        apiVersion='networking.istio.io/v1alpha3',
        kind='VirtualService',
        metadata=dict(
            name=_get_full_name(name, singleton),
        ),
        spec=dict(
            hosts=hosts,
            http=[
                dict(
                    match=[dict(port=port.number)],
                    route=[
                        dict(
                            destination=dict(
                                host=_get_full_name(name, singleton),
                                port=dict(number=port.number),
                            )
                        )
                    ],
                )
                for port in chain(public_ports, internal_ports)
            ],
            **gateways_mixin,
        ),
    )


def gateways(
    name: str,
    *,
    singleton: bool,
    domain: str,
    ports: List[Port],
):
    ports = [p for p in ports if p.type is PortType.PUBLIC]
    if not ports:
        return
    yield dict(
        apiVersion='networking.istio.io/v1alpha3',
        kind='Gateway',
        metadata=dict(
            name=_get_full_name(name, singleton),
        ),
        spec=dict(
            selector={'istio': 'ingressgateway'},
            servers=[
                dict(
                    port=dict(
                        name=port.name,
                        number=port.number,
                        protocol=port.protocol.value.upper(),
                    ),
                    hosts=[domain],
                )
                for port in ports
            ],
        ),
    )


def main() -> None:
    with os.fdopen(sys.stdin.fileno(), 'rb') as inp:
        request = CodeGeneratorRequest.FromString(inp.read())

    files_to_generate = set(request.file_to_generate)

    # entrypoints: Dict[str, EntryPoint] = {
    #     entry_point.name: entry_point
    #     for entry_point in iter_entry_points(group='harness.wires', name=None)
    # }

    response = CodeGeneratorResponse()
    for pf in request.proto_file:
        if pf.name not in files_to_generate:
            continue
        proto_file_path = Path(pf.name)
        dest_file_path = proto_file_path.parent.joinpath(
            'chart', 'templates', 'svc.yaml',
        )
        template_file = response.file.add()
        template_file.name = str(dest_file_path)

        service_name = 'whisper'
        repository = 'registry.acme.dev/team/whisper'
        singleton = False
        ports = [
            Port(
                protocol=Protocol.HTTP,
                name='http',
                number=80,
                type=PortType.PUBLIC,
            ),
            Port(
                protocol=Protocol.HTTP,
                name='metrics',
                number=9000,
                type=PortType.HEADLESS,
            ),
            Port(
                protocol=Protocol.GRPC,
                name='grpc',
                number=50051,
                type=PortType.INTERNAL,
            ),
            Port(
                protocol=Protocol.HTTP,
                name='monitor',
                number=50101,
                type=PortType.PRIVATE,
            ),
        ]
        domain = 'whisper.example.com'

        resources = list(chain(
            deployments(
                service_name,
                singleton=singleton,
                repository=repository,
                ports=ports,
            ),
            services(
                service_name,
                singleton=singleton,
                ports=ports,
            ),
            gateways(
                service_name,
                singleton=singleton,
                domain=domain,
                ports=ports,
            ),
            virtual_services(
                service_name,
                singleton=singleton,
                domain=domain,
                ports=ports,
            ),
        ))

        template_file.content = yaml.dump_all(resources)

        chart_file = response.file.add()
        chart_file.name = str(proto_file_path.parent.joinpath(
            'chart', 'Chart.yaml',
        ))
        chart_file.content = yaml.dump(chart(service_name))

    with os.fdopen(sys.stdout.fileno(), 'wb') as out:
        out.write(response.SerializeToString())
