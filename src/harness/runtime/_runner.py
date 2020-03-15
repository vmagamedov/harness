import asyncio
import argparse
from typing import Generic, TypeVar, Callable, Awaitable, List, Type
from contextlib import AsyncExitStack
from dataclasses import fields

from google.protobuf.json_format import ParseDict

from ..wires.base import Wire

from ._utils import load_config, graceful_exit
from ._validate import validate
from ._features import enable_metrics, enable_tracing


# Temporary decision to enable metrics and tracing by default. But maybe it
# would be better to make this [auto]configurable.
enable_metrics()
enable_tracing()


_CT = TypeVar("_CT")
_WI = TypeVar("_WI")
_WO = TypeVar("_WO")


class Runner(Generic[_CT, _WI, _WO]):
    def __init__(
        self,
        config_type: Type[_CT],
        wires_in_type: Type[_WI],
        wires_out_type: Type[_WO],
    ) -> None:
        self._config_type = config_type
        self._wires_in_type = wires_in_type
        self._wires_out_type = wires_out_type

        self._arg_parser = argparse.ArgumentParser()
        self._arg_parser.add_argument(
            "config",
            type=argparse.FileType("r", encoding="utf-8"),
            help="Configuration file in the YAML format",
        )
        self._arg_parser.add_argument(
            "--merge",
            default=None,
            type=argparse.FileType("r", encoding="utf-8"),
            help="Merge config with a file",
        )
        self._arg_parser.add_argument(
            "--patch",
            default=None,
            type=argparse.FileType("r", encoding="utf-8"),
            help="Patch config with a file",
        )

    async def _wrapper(
        self, main_func: Callable[[_CT, _WI], Awaitable[_WO]], config: _CT,
    ) -> None:
        async with AsyncExitStack() as stack:
            input_wires = {}
            for field in fields(self._wires_in_type):
                if config.HasField(field.name):
                    wire_config = getattr(config, field.name)
                    if isinstance(field.type, type) and issubclass(field.type, Wire):
                        wire_type = field.type
                    else:
                        # Optional[wire_type]
                        wire_type = field.type.__args__[0]
                        assert isinstance(wire_type, type) and issubclass(
                            wire_type, Wire
                        ), type(wire_type)
                    wire = wire_type()
                    wire.configure(wire_config)
                    await stack.enter_async_context(wire)
                else:
                    if isinstance(field.type, type) and issubclass(field.type, Wire):
                        raise RuntimeError(
                            f"Missing configuration for" f" required wire: {field.name}"
                        )
                    wire = None
                input_wires[field.name] = wire
            wires_in = self._wires_in_type(**input_wires)

            wires_out = await main_func(config, wires_in)

            if not isinstance(wires_out, self._wires_out_type):
                raise RuntimeError(
                    f"{main_func} returned invalid type: {type(wires_out)!r}; "
                    f"expected: {self._wires_out_type!r}"
                )

            waiters = set()
            output_wires = []
            for field in fields(self._wires_out_type):
                if not config.HasField(field.name):
                    continue
                wire = getattr(wires_out, field.name)
                wire_config = getattr(config, field.name)
                wire.configure(wire_config)
                await stack.enter_async_context(wire)
                waiters.add(wire.wait_closed())
                output_wires.append(wire)

            if output_wires:
                with graceful_exit(output_wires):
                    await asyncio.wait(
                        waiters, return_when=asyncio.FIRST_COMPLETED,
                    )

    def run(self, main_func: Callable[[_WI], Awaitable[_WO]], args: List[str]) -> int:
        args = self._arg_parser.parse_args(args[1:])

        with args.config:
            config_content = args.config.read()

        if args.merge is not None:
            with args.merge:
                merge_content = args.merge.read()
        else:
            merge_content = None

        if args.patch is not None:
            with args.patch:
                patch_content = args.patch.read()
        else:
            patch_content = None

        config_data = load_config(config_content, merge_content, patch_content)
        config = self._config_type()
        ParseDict(config_data, config)
        validate(config)

        asyncio.run(self._wrapper(main_func, config))
        return 0
