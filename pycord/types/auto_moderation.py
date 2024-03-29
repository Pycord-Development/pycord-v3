# cython: language_level=3
# Copyright (c) 2022-present Pycord Development
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

from typing import Literal

from typing_extensions import TypedDict

from .snowflake import Snowflake

AUTO_MODERATION_TRIGGER_TYPES = Literal[1, 3, 4, 5]
AUTO_MODERATION_KEYWORD_PRESET_TYPES = Literal[1, 2, 3]
AUTO_MODERATION_EVENT_TYPES = Literal[1]
AUTO_MODERATION_ACTION_TYPES = Literal[1, 2, 3]


class AutoModerationActionMetadata(TypedDict):
    channel_id: Snowflake
    duration_seconds: int


class AutoModerationAction(TypedDict):
    type: AUTO_MODERATION_ACTION_TYPES
    metadata: AutoModerationActionMetadata


class AutoModerationTriggerMetadata(TypedDict):
    keyword_filter: list[str]
    regex_patterns: list[str]
    presets: list[AUTO_MODERATION_KEYWORD_PRESET_TYPES]
    allow_list: list[str]
    mention_total_limit: int


class AutoModerationRule(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    name: str
    creator_id: Snowflake
    event_type: AUTO_MODERATION_EVENT_TYPES
    trigger_type: AUTO_MODERATION_TRIGGER_TYPES
    trigger_metadata: AutoModerationTriggerMetadata
    actions: list[AutoModerationAction]
    enabled: bool
    exempt_roles: list[Snowflake]
    exempt_channels: list[Snowflake]
