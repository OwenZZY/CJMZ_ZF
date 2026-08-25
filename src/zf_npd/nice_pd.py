from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence


def check_nice() -> bool:
    """
    This method checks if the input path decomposition is nice.
    :return:
    """
    raise NotImplementedError("interface skeleton pending")

def make_npd() -> None:
    """
    The method takes in path decomposition that is not nice, and construct a nice path decomposition
    :return:
    """
    raise NotImplementedError("interface skeleton pending")


# @dataclass(frozen=True)
class NicePD:
    k: int                              # len(bags) - 2
    width: int                          # the width of this path decomposition,
                                        # the max order of a bag - 1.
    bags: tuple[bytes, ...]             # length k+2, with two empty bags at both ends.
    ops: tuple[tuple[int, bool], ...]   # operations, where each pair consists of int that
                                        # represents a vertex and a bool representing if it is an insertion

    def __init__(self, bags: Sequence[Sequence[int]], n: int) -> None:
        masks = tuple(_to_mask(b, n) for b in bags)
        assert masks[0] == masks[-1] == b"\x00" * n, "sentinels must be empty"
        self.k, self.width, self.ops = _derive(masks, n)          # 断言 D2/D3/D4
        self.masks = masks
        object.__setattr__(self, "k", self.k)
        object.__setattr__(self, "width", self.width)
        object.__setattr__(self, "bags", self.masks)
        evs = ", ".join(f"({v}, {ins})" for v, ins in self.ops)
        object.__setattr__(self, "ops", evs)

    def __repr__(self) -> str:
        evs = ", ".join(f"({v}, {ins})" for v, ins in self.ops)
        return f"NicePD(k={self.k}, width={self.width}, ops=[{evs}])"


def _derive(masks: tuple[bytes, ...], n: int) -> tuple[int, int, tuple[tuple[int, bool], ...]]:
    ops: list[tuple[int, bool]] = []
    state = bytearray(n)                 # 0=未见 1=活跃 2=已遗忘
    width = -1
    k = len(masks) - 2
    for i in range(1, len(masks)):
        prev, cur = masks[i-1], masks[i]
        diff = [v for v in range(n) if prev[v] != cur[v]]
        assert len(diff) == 1, f"(D4) violated at transition {i-1} -> {i}: {diff}"
        v = diff[0]
        insert = cur[v] == 1
        if insert:
            assert state[v] != 2, f"(D2) vertex {v} reintroduced at bag {i}"
            state[v] = 1
        else:
            assert state[v] == 1, f"(D2) vertex {v} forgotten before introduction at bag {i}"
            state[v] = 2
        ops.append((v, insert))
        if i <= k:                       # 中间 bag X_1..X_k
            assert any(cur), f"(D3) bag {i} empty"
            width = max(width, cur.count(1) - 1)
    assert all(s == 2 for s in state), "(D2) some vertex never introduced"
    return k, width, tuple(ops)




def _to_mask(bag: Sequence[int], n: int) -> bytes:
    m = bytearray(n)
    for v in bag:
        assert 0 <= v < n, f"vertex {v} out of range [0, {n})"
        m[v] = 1
    return bytes(m)          # 构造边界一次性转 bytes，之后不可变