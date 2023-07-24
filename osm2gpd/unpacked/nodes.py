from dataclasses import dataclass
from itertools import accumulate
from typing import Generator, Iterator, Self, Sequence

from osm2gpd.proto import PrimitiveGroup

from .base import BaseGroup

__all__ = ["NodesGroup"]


@dataclass(repr=False)
class NodesGroup(BaseGroup):
    lat: list[float]
    lon: list[float]

    @classmethod
    def from_dense_group(
        cls,
        group: PrimitiveGroup,
        string_table: list[str],
        *,
        granularity: float,
        lat_offset: float,
        lon_offset: float,
    ) -> Self:
        return cls(
            ids=list(accumulate(group.dense.id)),
            lat=[
                (x * granularity + lat_offset) * 1e-9
                for x in accumulate(group.dense.lat)
            ],
            lon=[
                (x * granularity + lon_offset) * 1e-9
                for x in accumulate(group.dense.lon)
            ],
            tags=dict(_parse_dense_tags(group.dense.keys_vals, string_table)),
            version=list(group.dense.denseinfo.version),
            visible=list(_visible(group.dense.denseinfo.visible, len(group.dense.id))),
            changeset=list(accumulate(group.dense.denseinfo.changeset)),
        )


def _parse_dense_tags(
    keys_vals: Sequence[int], string_table: list[str]
) -> Generator[tuple[int, dict[str, str]], None, None]:
    node_idx = 0
    kv_idx = 0

    while kv_idx < len(keys_vals):
        tags = dict()
        while keys_vals[kv_idx] != 0:
            k = keys_vals[kv_idx]
            v = keys_vals[kv_idx + 1]
            kv_idx += 2
            tags[string_table[k]] = string_table[v]

        if len(tags) > 0:
            yield node_idx, tags

        kv_idx += 1
        node_idx += 1


def _visible(values: Sequence[bool], length: int) -> Iterator[bool]:
    if len(values) == length:
        return iter(values)
    elif len(values) == 0:
        return (True for _ in range(length))
    else:
        raise ValueError("Invalid length of 'visible' values")
