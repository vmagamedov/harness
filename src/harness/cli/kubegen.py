import hashlib
from io import BytesIO
from typing import List, Optional
from base64 import b64encode
from itertools import chain
from contextlib import closing
from dataclasses import dataclass

import yaml

from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.json_format import ParseDict
from google.protobuf.message_factory import GetMessages

from .. import wire_pb2, net_pb2
from ..config import translate_descriptor, WireSpec
from ..runtime._utils import load_config
from ..runtime._validate import validate

from .utils import load_descriptor_set, get_configuration


@dataclass
class Runtime:
    entrypoint: List[str]


RUNTIMES = {
    "python": Runtime(entrypoint=["python3", "/app/entrypoint.py"]),
}


def _ver(content_bytes):
    return hashlib.new("sha1", content_bytes).hexdigest()[:8]


@dataclass
class Socket:
    host: str
    port: int
    _protocol: wire_pb2.Mark.Protocol

    def is_tcp(self):
        return self._protocol == wire_pb2.Mark.TCP

    def is_http(self):
        return self._protocol == wire_pb2.Mark.HTTP

    def is_grpc(self):
        return self._protocol == wire_pb2.Mark.GRPC


@dataclass
class Input:
    _wire: WireSpec
    socket: Optional[Socket] = None

    @property
    def name(self):
        return self._wire.name

    def is_localhost(self):
        return self._wire.value.input.reach == wire_pb2.Input.LOCALHOST

    def is_namespace(self):
        return self._wire.value.input.reach == wire_pb2.Input.NAMESPACE

    def is_cluster(self):
        return self._wire.value.input.reach == wire_pb2.Input.CLUSTER

    def is_external(self):
        return self._wire.value.input.reach == wire_pb2.Input.EXTERNAL


@dataclass
class Output:
    _wire: WireSpec
    socket: Optional[Socket] = None

    @property
    def name(self):
        return self._wire.name

    def is_private(self):
        return self._wire.value.output.expose == wire_pb2.Output.PRIVATE

    def is_internal(self):
        return self._wire.value.output.expose == wire_pb2.Output.INTERNAL

    def is_public(self):
        return self._wire.value.output.expose == wire_pb2.Output.PUBLIC

    def is_headless(self):
        return self._wire.value.output.expose == wire_pb2.Output.HEADLESS


@dataclass
class HostPath:
    name: str
    path: str
    type: str


@dataclass
class Context:
    _container: wire_pb2.Service.Container

    name: str
    inputs: List[Input]
    outputs: List[Output]
    host_paths: List[HostPath]
    entrypoint: List[str]
    config_content: str
    config_hash: str
    secret_merge_content: Optional[str]
    secret_merge_hash: Optional[str]
    secret_patch_content: Optional[str]
    secret_patch_hash: Optional[str]

    # pass-through
    version: str
    instance: Optional[str]
    namespace: str
    base_domain: Optional[str]

    # constants
    config_volume = "config"
    secret_merge_volume = "config-merge"
    secret_patch_volume = "config-patch"

    @property
    def repository(self):
        return self._container.repository

    def resources(self):
        data = dict()
        if self._container.resources.requests:
            requests = data["requests"] = {}
            if self._container.resources.requests.cpu:
                requests["cpu"] = self._container.resources.requests.cpu
            if self._container.resources.requests.memory:
                requests["memory"] = self._container.resources.requests.memory
        if self._container.resources.limits:
            limits = data["limits"] = {}
            if self._container.resources.limits.cpu:
                limits["cpu"] = self._container.resources.limits.cpu
            if self._container.resources.limits.memory:
                limits["memory"] = self._container.resources.limits.memory
        return data

    @property
    def config_name(self):
        return self.full_name("config", self.config_hash)

    @property
    def secret_merge_name(self):
        return self.full_name("config-merge", self.secret_merge_hash)

    @property
    def secret_patch_name(self):
        return self.full_name("config-patch", self.secret_merge_hash)

    def full_name(self, *suffix: str):
        parts = [self.name]
        if self.instance is not None:
            parts.append(self.instance)
        parts.extend(suffix)
        return "-".join(parts)

    def labels(self):
        labels = {"app.kubernetes.io/name": self.name}
        if self.instance is not None:
            labels["app.kubernetes.io/instance"] = self.instance
        return labels

    @property
    def public_domain(self):
        if self.base_domain is not None:
            if self.instance is None:
                sub_domain = self.name
            else:
                sub_domain = f"{self.name}-{self.instance}"
            return f"{sub_domain}.{self.base_domain}"


def get_socket(wire: WireSpec, message_classes, config: Message) -> Optional[Socket]:
    if wire.optional:
        if not config.HasField(wire.name):
            return None
    else:
        assert config.HasField(wire.name), f"Config unset: {wire.name}"

    wire_type = message_classes[wire.type]
    socket_type_fd = next(
        (
            fd
            for fd in wire_type.DESCRIPTOR.fields
            if fd.type == FieldDescriptor.TYPE_MESSAGE
            and fd.message_type.full_name == net_pb2.Socket.DESCRIPTOR.full_name
        ),
        None,
    )
    if socket_type_fd is None:
        return None

    protocol = wire_pb2.Mark.TCP
    for _, option in socket_type_fd.GetOptions().ListFields():
        if isinstance(option, wire_pb2.Mark):
            protocol = option.protocol

    wire_value = getattr(config, wire.name)
    socket_value = getattr(wire_value, socket_type_fd.name)
    return Socket(host=socket_value.host, port=socket_value.port, _protocol=protocol)


def get_context(
    *,
    proto_file,
    proto_path,
    runtime,
    config_bytes,
    secret_merge_bytes=None,
    secret_patch_bytes=None,
    passthrough=None,
):
    runtime = RUNTIMES[runtime]

    descriptor_set = load_descriptor_set(proto_file, proto_path)
    (file_descriptor,) = (f for f in descriptor_set.file if proto_file.endswith(f.name))

    config_hash = _ver(config_bytes)
    config_content = config_bytes.decode("utf-8")

    if secret_merge_bytes is not None:
        secret_merge_hash = _ver(secret_merge_bytes)
        secret_merge_content = secret_merge_bytes.decode("utf-8")
    else:
        secret_merge_hash = None
        secret_merge_content = None

    if secret_patch_bytes is not None:
        secret_patch_hash = _ver(secret_patch_bytes)
        secret_patch_content = secret_patch_bytes.decode("utf-8")
    else:
        secret_patch_hash = None
        secret_patch_content = None

    message_classes = GetMessages(descriptor_set.file)

    config_descriptor = get_configuration(file_descriptor)
    if config_descriptor is None:
        raise Exception(f"Configuration message not found in the {proto_file}")

    config_data = load_config(
        config_content, secret_merge_content, secret_patch_content,
    )

    config_full_name = ".".join(
        filter(None, (file_descriptor.package, config_descriptor.name))
    )
    config_cls = message_classes[config_full_name]
    config = config_cls()
    ParseDict(config_data, config)
    validate(config)

    config_spec = translate_descriptor(config_cls.DESCRIPTOR)

    inputs = []
    outputs = []
    for wire in config_spec.wires:
        wire_type = wire.value.WhichOneof("type")
        if wire_type == "input":
            inputs.append(
                Input(_wire=wire, socket=get_socket(wire, message_classes, config))
            )
        elif wire_type == "output":
            outputs.append(
                Output(_wire=wire, socket=get_socket(wire, message_classes, config))
            )

    host_paths = []
    for wire in config_spec.wires:
        if wire.type == "harness.logging.Syslog":
            host_paths.append(HostPath(name="syslog", path="/dev/log", type="Socket"))

    assert config_spec.service.name
    return Context(
        name=config_spec.service.name,
        inputs=inputs,
        outputs=outputs,
        _container=config_spec.service.container,
        host_paths=host_paths,
        entrypoint=runtime.entrypoint,
        config_content=config_content,
        config_hash=config_hash,
        secret_merge_content=secret_merge_content,
        secret_merge_hash=secret_merge_hash,
        secret_patch_content=secret_patch_content,
        secret_patch_hash=secret_patch_hash,
        **(passthrough or {}),
    )


def istio_type(socket: Socket):
    if socket.is_tcp():
        return "TCP"
    elif socket.is_http():
        return "HTTP"
    elif socket.is_grpc():
        return "GRPC"
    else:
        return "TCP"


def public_port(socket: Socket) -> int:
    if socket.is_http():
        return 80
    elif socket.is_grpc():
        return 50051
    else:
        return socket.port


def istio_name(socket, suffix):
    if socket.is_tcp():
        name = "tcp"
    elif socket.is_http():
        name = "http"
    elif socket.is_grpc():
        name = "grpc"
    else:
        name = "tcp"
    return name + "-" + suffix


def gen_deployments(ctx: Context):
    match_labels = ctx.labels()

    pod_labels = ctx.labels()
    pod_labels["app.kubernetes.io/version"] = ctx.version

    annotations = {"sidecar.istio.io/inject": "true"}

    command = ctx.entrypoint + ["/etc/config/config.yaml"]
    if ctx.secret_merge_content is not None:
        command.extend(["--merge", "/etc/config-merge/config.yaml"])
    if ctx.secret_patch_content is not None:
        command.extend(["--patch", "/etc/config-patch/config.yaml"])

    container = dict(
        name="app",
        image=f"{ctx.repository}:{ctx.version}",
        command=command,
        securityContext=dict(runAsUser=1000),
        volumeMounts=[dict(mountPath="/etc/config", name=ctx.config_volume)],
    )
    if ctx.secret_merge_content is not None:
        container["volumeMounts"].append(
            dict(mountPath="/etc/config-merge", name=ctx.secret_merge_volume)
        )
    if ctx.secret_patch_content is not None:
        container["volumeMounts"].append(
            dict(mountPath="/etc/config-patch", name=ctx.secret_patch_volume)
        )
    for host_path in ctx.host_paths:
        container["volumeMounts"].append(
            dict(mountPath=host_path.path, name=host_path.name)
        )

    if ctx.outputs:
        container_ports = container["ports"] = []
        for wire in ctx.outputs:
            if wire.socket is not None:
                container_port = dict(
                    name=istio_name(wire.socket, wire.name),
                    containerPort=wire.socket.port,
                )
                container_ports.append(container_port)

    for wire in ctx.outputs:
        if not wire.is_public() and not wire.is_internal() or wire.socket is None:
            continue
        if wire.socket.is_http():
            container["readinessProbe"] = dict(
                httpGet=dict(
                    path="/_/health", port=istio_name(wire.socket, wire.name),
                ),
            )
        elif wire.socket.is_grpc():
            container["readinessProbe"] = dict(
                exec=dict(
                    command=[
                        "grpc_health_probe",
                        "-addr",
                        f"localhost:{wire.socket.port}",
                    ],
                ),
            )

    resources = ctx.resources()
    if resources:
        container["resources"] = resources

    volumes = [
        dict(name=ctx.config_volume, configMap=dict(name=ctx.config_name)),
    ]
    if ctx.secret_merge_content is not None:
        volumes.append(
            dict(
                name=ctx.secret_merge_volume,
                secret=dict(secretName=ctx.secret_merge_name),
            )
        )
    if ctx.secret_patch_content is not None:
        volumes.append(
            dict(
                name=ctx.secret_patch_volume,
                secret=dict(secretName=ctx.secret_patch_name),
            )
        )
    for host_path in ctx.host_paths:
        volumes.append(
            dict(
                name=host_path.name,
                hostPath=dict(path=host_path.path, type=host_path.type),
            )
        )

    yield dict(
        apiVersion="apps/v1",
        kind="Deployment",
        metadata=dict(name=ctx.full_name(), namespace=ctx.namespace),
        spec=dict(
            selector=dict(matchLabels=match_labels),
            template=dict(
                metadata=dict(labels=pod_labels, annotations=annotations),
                spec=dict(containers=[container], volumes=volumes),
            ),
        ),
    )


def gen_services(ctx: Context):
    def port(value: Output):
        return dict(
            name=istio_name(value.socket, value.name),
            port=public_port(value.socket),
            targetPort=istio_name(value.socket, value.name),
        )

    regular_outputs = [
        i
        for i in ctx.outputs
        if (i.is_internal() or i.is_public()) and i.socket is not None
    ]
    headless_outputs = [
        i for i in ctx.outputs if i.is_headless() and i.socket is not None
    ]
    if regular_outputs:
        yield dict(
            apiVersion="v1",
            kind="Service",
            metadata=dict(name=ctx.full_name(), namespace=ctx.namespace),
            spec=dict(ports=[port(i) for i in regular_outputs], selector=ctx.labels()),
        )
    if headless_outputs:
        yield dict(
            apiVersion="v1",
            kind="Service",
            metadata=dict(name=ctx.full_name("headless"), namespace=ctx.namespace),
            spec=dict(
                clusterIP="None",
                ports=[port(i) for i in headless_outputs],
                selector=ctx.labels(),
            ),
        )


def gen_virtualservices(ctx: Context):
    internal_outputs = [
        i for i in ctx.outputs if i.is_internal() and i.socket is not None
    ]
    public_outputs = [i for i in ctx.outputs if i.is_public() and i.socket is not None]

    hosts = []
    if internal_outputs:
        hosts.append(ctx.full_name())
    if public_outputs and ctx.public_domain:
        hosts.append(ctx.public_domain)
    if not hosts:
        return

    spec = dict(
        hosts=hosts,
        http=[
            dict(
                match=[dict(port=public_port(i.socket))],
                route=[
                    dict(
                        destination=dict(
                            host=ctx.full_name(),
                            port=dict(number=public_port(i.socket)),
                        )
                    )
                ],
            )
            for i in chain(public_outputs, internal_outputs)
        ],
    )
    if public_outputs:
        spec["gateways"] = [ctx.full_name(), "mesh"]

    yield dict(
        apiVersion="networking.istio.io/v1alpha3",
        kind="VirtualService",
        metadata=dict(name=ctx.full_name(), namespace=ctx.namespace),
        spec=spec,
    )


def gen_gateways(ctx: Context):
    public_outputs = [i for i in ctx.outputs if i.is_public() and i.socket is not None]
    if not (public_outputs and ctx.public_domain):
        return

    yield dict(
        apiVersion="networking.istio.io/v1alpha3",
        kind="Gateway",
        metadata=dict(name=ctx.full_name(), namespace=ctx.namespace),
        spec=dict(
            selector={"istio": "ingressgateway"},
            servers=[
                dict(
                    port=dict(
                        name=istio_name(out.socket, out.name),
                        number=public_port(out.socket),
                        protocol=istio_type(out.socket),
                    ),
                    hosts=[ctx.public_domain],
                )
                for out in public_outputs
            ],
        ),
    )


def gen_sidecars(ctx: Context):
    hosts = ["istio-system/*"]
    for inp in ctx.inputs:
        if inp.socket is None:
            continue
        if inp.is_namespace():
            assert ctx.namespace
            host = inp.socket.host
            hosts.append(f"./{host}.{ctx.namespace}.svc.cluster.local")
        elif inp.is_cluster():
            host = inp.socket.host
            hosts.append(f"*/{host}")
        elif inp.is_external():
            host = inp.socket.host
            hosts.append(f"./{host}")
        else:
            continue
    yield dict(
        apiVersion="networking.istio.io/v1alpha3",
        kind="Sidecar",
        metadata=dict(name=ctx.full_name(), namespace=ctx.namespace),
        spec=dict(
            egress=[dict(hosts=hosts)], workloadSelector=dict(labels=ctx.labels()),
        ),
    )


def gen_serviceentries(ctx: Context):
    for inp in ctx.inputs:
        if not inp.is_external():
            continue
        yield dict(
            apiVersion="networking.istio.io/v1alpha3",
            kind="ServiceEntry",
            metadata=dict(name=ctx.full_name(inp.name), namespace=ctx.namespace),
            spec=dict(
                hosts=[inp.socket.host],
                location="MESH_EXTERNAL",
                ports=[dict(number=inp.socket.port, protocol=istio_type(inp.socket))],
            ),
        )


def gen_configmaps(ctx: Context):
    yield dict(
        apiVersion="v1",
        kind="ConfigMap",
        metadata=dict(name=ctx.config_name, namespace=ctx.namespace),
        data={"config.yaml": ctx.config_content},
    )


def gen_secrets(ctx: Context):
    def b64(string):
        return b64encode(string.encode("utf-8")).decode("ascii")

    if ctx.secret_merge_content is not None:
        yield dict(
            apiVersion="v1",
            kind="Secret",
            type="Opaque",
            metadata=dict(name=ctx.secret_merge_name, namespace=ctx.namespace),
            data={"config.yaml": b64(ctx.secret_merge_content)},
        )
    if ctx.secret_patch_content is not None:
        yield dict(
            apiVersion="v1",
            kind="Secret",
            type="Opaque",
            metadata=dict(name=ctx.secret_patch_name, namespace=ctx.namespace),
            data={"config.yaml": b64(ctx.secret_patch_content)},
        )


def kube_gen(
    runtime: str,
    proto: str,
    config: BytesIO,
    version: str,
    *,
    proto_path: List[str],
    secret_merge: Optional[BytesIO] = None,
    secret_patch: Optional[BytesIO] = None,
    instance: Optional[str] = None,
    namespace: Optional[str] = None,
    base_domain: Optional[str] = None,
) -> None:
    # configuration
    with closing(config):
        config_bytes = config.read()

    # merge
    if secret_merge is not None:
        with closing(secret_merge):
            secret_merge_bytes = secret_merge.read()
    else:
        secret_merge_bytes = None

    # patch
    if secret_patch is not None:
        with closing(secret_patch):
            secret_patch_bytes = secret_patch.read()
    else:
        secret_patch_bytes = None

    ctx = get_context(
        proto_file=proto,
        proto_path=proto_path,
        runtime=runtime,
        config_bytes=config_bytes,
        secret_merge_bytes=secret_merge_bytes,
        secret_patch_bytes=secret_patch_bytes,
        passthrough=dict(
            version=version,
            instance=instance,
            namespace=namespace,
            base_domain=base_domain,
        ),
    )
    resources = list(
        chain(
            gen_configmaps(ctx),
            gen_secrets(ctx),
            gen_deployments(ctx),
            gen_services(ctx),
            gen_gateways(ctx),
            gen_virtualservices(ctx),
            gen_serviceentries(ctx),
            gen_sidecars(ctx),
        )
    )
    print(yaml.dump_all(resources))
