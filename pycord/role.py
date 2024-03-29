# cython: language_level=3
# Copyright (c) 2021-present Pycord Development
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE
from __future__ import annotations

from typing import TYPE_CHECKING

from .color import Color
from .flags import Permissions
from .snowflake import Snowflake

if TYPE_CHECKING:
    from .state import State

from .missing import MISSING, Maybe, MissingEnum
from .types import Role as DiscordRole, RoleTags as DiscordRoleTags


class RoleTags:
    __slots__ = ('bot_id', 'integration_id', 'premium_subscriber')

    def __init__(self, data: DiscordRoleTags) -> None:
        self.bot_id: MissingEnum | Snowflake = (
            Snowflake(data.get('bot_id'))
            if data.get('bot_id', MISSING) is not MISSING
            else MISSING
        )
        self.integration_id: MissingEnum | Snowflake = (
            Snowflake(data.get('integration_id'))
            if data.get('integration_id', MISSING) is not MISSING
            else MISSING
        )
        self.premium_subscriber: MissingEnum | None = data.get(
            'premium_subscriber', MISSING
        )


class Role:
    __slots__ = (
        '_state',
        '_tags',
        'id',
        'name',
        'color',
        'hoist',
        'icon',
        'unicode_emoji',
        'position',
        'permissions',
        'managed',
        'mentionable',
        'tags',
    )

    def __init__(self, data: DiscordRole, state: State) -> None:
        self._state = state
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['name']
        self.color: Color = Color(data['color'])
        self.hoist: bool = data['hoist']
        self.icon: str | None | MissingEnum = data.get('icon', MISSING)
        self.unicode_emoji: str | None | MissingEnum = data.get(
            'unicode_emoji', MISSING
        )
        self.position: int = data['position']
        self.permissions: Permissions = Permissions.from_value(data['permissions'])
        self.managed: bool = data['managed']
        self.mentionable: bool = data['mentionable']
        self._tags: dict[str, str | None] | MissingEnum = data.get('tags', MISSING)
        self.tags: RoleTags | MissingEnum = (
            RoleTags(self._tags) if self._tags is not MISSING else MISSING
        )
