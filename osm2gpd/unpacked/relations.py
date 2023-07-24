from dataclasses import dataclass
from itertools import accumulate
from typing import Self

from osm2gpd.proto import PrimitiveGroup
from osm2gpd.tags import get_tags

from .base import BaseGroup

__all__ = ["RelationGroup"]


@dataclass(repr=False)
class RelationGroup(BaseGroup):
    member_types: list[list[str]]
    member_roles: list[list[str]]
    member_ids: list[list[int]]

    @classmethod
    def from_primitive_group(
        cls, group: PrimitiveGroup, string_table: list[str]
    ) -> Self:
        ids: list[int] = []
        versions: list[int] = []
        member_ids: list[list[int]] = []
        member_types: list[list[str]] = []
        member_roles: list[list[str]] = []
        tags: dict[int, dict[str, str]] = {}
        visible: list[bool] = []
        changeset: list[int] = []

        for i, relation in enumerate(group.relations):
            ids.append(relation.id)

            member_types.append(
                [relation.MemberType.keys()[type_].lower() for type_ in relation.types]
            )
            member_ids.append(list(accumulate(relation.memids)))
            member_roles.append([string_table[sid] for sid in relation.roles_sid])

            _tags = get_tags(relation, string_table)
            if len(_tags) > 0:
                tags[i] = _tags

            # fixme: add optional here
            versions.append(relation.info.version)
            visible.append(relation.info.visible)
            changeset.append(relation.info.changeset)

        return cls(
            ids=ids,
            tags=tags,
            version=versions,
            changeset=changeset,
            visible=visible,
            member_ids=member_ids,
            member_roles=member_roles,
            member_types=member_types,
        )
