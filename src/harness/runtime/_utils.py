import signal
import asyncio
from typing import Collection, List, Optional, Iterator, Any
from contextlib import contextmanager

import yaml
from jsonpatch import JsonPatch
from json_merge_patch import merge

from ..wires.base import Wire


def load_config(config_content, merge_content=None, patch_content=None):
    config_data = yaml.safe_load(config_content)
    if config_data is None:
        config_data = {}
    if not isinstance(config_data, dict):
        raise SystemExit(f"Invalid configuration format: {type(config_data)!r}")

    if merge_content is not None:
        merge_data = yaml.safe_load(merge_content)
        config_data = merge(config_data, merge_data)

    if patch_content is not None:
        patch_data = yaml.safe_load(patch_content)
        json_patch = JsonPatch(patch_data)
        config_data = json_patch.apply(config_data)
    return config_data


def _first_stage(sig_num: signal.Signals, wires: Collection[Wire]) -> None:
    fail = False
    for wire in wires:
        try:
            wire.close()
        except RuntimeError:
            # probably wire wasn't started yet
            fail = True
    if fail:
        # using second stage in case of error will ensure that non-closed
        # wire wont start later
        _second_stage(sig_num)


def _second_stage(sig_num: signal.Signals) -> None:
    raise SystemExit(128 + sig_num)


def _exit_handler(
    sig_num: signal.Signals, wires: Collection[Wire], flag: List[bool],
) -> None:
    if flag:
        _second_stage(sig_num)
    else:
        _first_stage(sig_num, wires)
        flag.append(True)


@contextmanager
def graceful_exit(
    wires: Collection[Wire],
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    signals: Collection[int] = (signal.SIGINT, signal.SIGTERM),
) -> Iterator[None]:
    loop = loop or asyncio.get_event_loop()
    signals = set(signals)
    flag: List[bool] = []
    for sig_num in signals:
        loop.add_signal_handler(sig_num, _exit_handler, sig_num, wires, flag)
    try:
        yield
    finally:
        for sig_num in signals:
            loop.remove_signal_handler(sig_num)


class Buffer:
    def __init__(self) -> None:
        self._lines: List[str] = []
        self._indent = 0

    def add(self, string: str, *args: Any, **kwargs: Any) -> None:
        line = " " * self._indent * 4 + string.format(*args, **kwargs)
        self._lines.append(line.rstrip(" "))

    @contextmanager
    def indent(self) -> Iterator[None]:
        self._indent += 1
        try:
            yield
        finally:
            self._indent -= 1

    def content(self) -> str:
        return "\n".join(self._lines) + "\n"

    @property
    def position(self) -> int:
        return len(self._lines)
