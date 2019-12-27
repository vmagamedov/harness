import os
import sys
from enum import Enum
from typing import List
from pathlib import Path
from itertools import chain
from dataclasses import dataclass

import yaml

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorResponse

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


def _get_full_name(name: str, singleton: bool):
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


def _k8s_port(wire: Wire):
    return f'{{{{ .Values.{wire.name}.bind.port }}}}'


def _k8s_container_port(wire: Wire):
    k8s_port = dict(
        name=wire.protocol.istio_name(wire.name),
        containerPort=_k8s_port(wire),
    )
    protocol = wire.protocol.k8s_name()
    if protocol != 'TCP':
        k8s_port['protocol'] = protocol
    return k8s_port


def deployments(
    name: str,
    *,
    singleton: bool,
    repository: str,
    ingress: List[Wire],
):
    labels = _get_labels(name, singleton)
    labels['app.kubernetes.io/version'] = '{{ .Values.version }}'

    if ingress:
        ports_mixin = dict(ports=list(map(_k8s_container_port, ingress)))
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


def _k8s_svc_port(wire: Wire):
    k8s_port = dict(
        name=wire.protocol.istio_name(wire.name),
        port=_k8s_port(wire),
        targetPort=wire.protocol.istio_name(wire.name),
    )
    protocol = wire.protocol.k8s_name()
    if protocol != 'TCP':
        k8s_port['protocol'] = protocol
    return k8s_port


def services(
    name: str,
    singleton: bool,
    ingress: List[Wire],
):
    regular_wires = [
        p for p in ingress
        if p.visibility in {Visibility.INTERNAL, Visibility.PUBLIC}
    ]
    headless_wires = [
        p for p in ingress if p.visibility is Visibility.HEADLESS
    ]

    if regular_wires:
        yield dict(
            apiVersion='v1',
            kind='Service',
            metadata=dict(
                name=_get_full_name(name, singleton),
            ),
            spec=dict(
                ports=list(map(_k8s_svc_port, regular_wires)),
                selector=_get_labels(name, singleton),
            ),
        )
    if headless_wires:
        yield dict(
            apiVersion='v1',
            kind='Service',
            metadata=dict(
                name=_get_full_name(name, singleton) + '-headless',
            ),
            spec=dict(
                clusterIP='None',
                ports=list(map(_k8s_svc_port, headless_wires)),
                selector=_get_labels(name, singleton),
            ),
        )


def _public_domain(name: str, singleton: bool):
    if singleton:
        return f'{name}.{{{{ .Values.baseDomain }}}}'
    else:
        return f'{name}-{{{{ .Release.Name }}}}.{{{{ .Values.baseDomain }}}}'


def virtual_services(
    name: str,
    *,
    singleton: bool,
    ingress: List[Wire],
):
    internal_wires = [w for w in ingress if w.visibility is Visibility.INTERNAL]
    public_wires = [w for w in ingress if w.visibility is Visibility.PUBLIC]
    if not internal_wires and not public_wires:
        return

    hosts = []
    if internal_wires:
        hosts.append(_get_full_name(name, singleton))
    if public_wires:
        hosts.append(_public_domain(name, singleton))

    if public_wires:
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
                    match=[dict(port=_k8s_port(wire))],
                    route=[
                        dict(
                            destination=dict(
                                host=_get_full_name(name, singleton),
                                port=dict(number=_k8s_port(wire)),
                            )
                        )
                    ],
                )
                for wire in chain(public_wires, internal_wires)
            ],
            **gateways_mixin,
        ),
    )


def gateways(
    name: str,
    *,
    singleton: bool,
    ingress: List[Wire],
):
    ingress = [w for w in ingress if w.visibility is Visibility.PUBLIC]
    if not ingress:
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
                        number=_k8s_port(wire),
                        protocol=wire.protocol.istio_type(),
                    ),
                    hosts=[_public_domain(name, singleton)],
                )
                for wire in ingress
            ],
        ),
    )


def sidecars(name: str, *, singleton: bool, egress: List[Wire]):
    hosts = ['istio-system/*']
    for wire in egress:
        if wire.access is Accessibility.NAMESPACE:
            hosts.append(
                f'./{{{{ .Values.{wire.name}.address.host }}}}'
                f'.{{{{ .Release.Namespace }}}}'
                f'.svc.cluster.local'
            )
        elif wire.access is Accessibility.CLUSTER:
            hosts.append(
                f'*/{{{{ .Values.{wire.name}.address.host }}}}'
            )
        elif wire.access is Accessibility.EXTERNAL:
            hosts.append(
                f'./{{{{ .Values.{wire.name}.address.host }}}}'
            )
        else:
            continue
    yield dict(
        apiVersion='networking.istio.io/v1alpha3',
        kind='Sidecar',
        metadata=dict(
            name=_get_full_name(name, singleton),
        ),
        spec=dict(
            egress=[dict(
                hosts=hosts,
            )],
            workloadSelector=dict(
                labels=_get_labels(name, singleton),
            ),
        ),
    )


def service_entries(name: str, *, singleton: bool, egress: List[Wire]):
    for wire in egress:
        if wire.access is not Accessibility.EXTERNAL:
            continue
        yield dict(
            apiVersion='networking.istio.io/v1alpha3',
            kind='ServiceEntry',
            metadata=dict(
                name=_get_full_name(name, singleton) + '-' + wire.name,
            ),
            spec=dict(
                hosts=[f'{{{{ .Values.{wire.name}.address.host }}}}'],
                location='MESH_EXTERNAL',
                ports=[dict(
                    number=f'{{{{ .Values.{wire.name}.address.port }}}}',
                    protocol=wire.protocol.istio_type(),
                )],
            ),
        )


def main() -> None:
    with os.fdopen(sys.stdin.fileno(), 'rb') as inp:
        request = CodeGeneratorRequest.FromString(inp.read())

    files_to_generate = set(request.file_to_generate)

    response = CodeGeneratorResponse()
    for pf in request.proto_file:
        if pf.name not in files_to_generate:
            continue

        service_name = None
        repository = None
        singleton = False

        ingress = []
        egress = []

        for mt in pf.message_type:
            for _, opt in mt.options.ListFields():
                if isinstance(opt, HarnessService):
                    service_name = opt.name
                    repository = opt.repository
                    if opt.release == HarnessService.SINGLE:
                        singleton = True
                    elif opt.release == HarnessService.MULTI:
                        singleton = False
                    else:
                        raise NotImplementedError(opt.release)

            for f in mt.field:
                for _, opt in f.options.ListFields():
                    if isinstance(opt, HarnessWire):
                        if opt.WhichOneof('type') == 'input':
                            egress.append(Wire(
                                f.name,
                                f.type_name,
                                Visibility(opt.visibility),
                                Protocol(opt.protocol),
                                Accessibility(opt.access),
                            ))
                        elif opt.WhichOneof('type') == 'output':
                            ingress.append(Wire(
                                f.name,
                                f.type_name,
                                Visibility(opt.visibility),
                                Protocol(opt.protocol),
                                Accessibility(opt.access),
                            ))

        if not service_name or not repository:
            continue

        proto_file_path = Path(pf.name)
        dest_file_path = proto_file_path.parent.joinpath(
            'chart', 'templates', 'svc.yaml',
        )
        template_file = response.file.add()
        template_file.name = str(dest_file_path)

        resources = list(chain(
            deployments(
                service_name,
                singleton=singleton,
                repository=repository,
                ingress=ingress,
            ),
            services(
                service_name,
                singleton=singleton,
                ingress=ingress,
            ),
            gateways(
                service_name,
                singleton=singleton,
                ingress=ingress,
            ),
            virtual_services(
                service_name,
                singleton=singleton,
                ingress=ingress,
            ),
            service_entries(
                service_name,
                singleton=singleton,
                egress=egress,
            ),
            sidecars(
                service_name,
                singleton=singleton,
                egress=egress,
            ),
        ))

        template_file.content = (
            yaml.dump_all(resources)
            .replace("'{{ ", "{{ ")
            .replace(" }}'", " }}")
        )

        chart_file = response.file.add()
        chart_file.name = str(proto_file_path.parent.joinpath(
            'chart', 'Chart.yaml',
        ))
        chart_file.content = yaml.dump(chart(service_name))

    with os.fdopen(sys.stdout.fileno(), 'wb') as out:
        out.write(response.SerializeToString())
