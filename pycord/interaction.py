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
from .errors import InteractionException
from .embed import Embed
from .message import Message
from .undefined import UNDEFINED, UndefinedType
from .snowflake import Snowflake
from .types import Interaction as InteractionData, INTERACTION_DATA
from .member import Member
from .user import User

if TYPE_CHECKING:
    from .state import State


class Interaction:
    def __init__(self, data: InteractionData, state: State, response: bool = False) -> None:
        self._state = state
        if response:
            self.response = InteractionResponse(self)
        self.id = Snowflake(data['id'])
        self.application_id = Snowflake(data['application_id'])
        self.type = data['type']
        self.data: INTERACTION_DATA | UndefinedType = data.get('data', UNDEFINED)
        _guild_id = data.get('guild_id')
        self.guild_id: Snowflake | UndefinedType = Snowflake(_guild_id) if _guild_id is not None else UNDEFINED
        _channel_id = data.get('channel_id')
        self.channel_id: Snowflake | UndefinedType = Snowflake(_channel_id) if _channel_id is not None else UNDEFINED
        _member = data.get('member')
        self.member = Member(_member, state) if _member is not None else UNDEFINED
        _user = data.get('user')
        self.user = User(_user, state) if _user is not None else UNDEFINED
        self.token = data['token']
        self.version = data['version']
        _message = data.get('message')
        self.message: Message | UndefinedType = Message(_message, state) if _message is not None else UNDEFINED
        self.app_permissions: str | UndefinedType = data.get('app_permissions', UNDEFINED)
        self.locale: str | UndefinedType = data.get('locale', UNDEFINED)
        self.guild_locale: str | UndefinedType = data.get('guild_locale', UNDEFINED)

    @property
    def resp(self) -> InteractionResponse:
        return self.response


class InteractionResponse:
    def __init__(self, parent: Interaction) -> None:
        self._parent = parent
        self.responded: bool = False

    async def send(
        self,
        content: str,
        tts: bool = False,
        embeds: list[Embed] = [],
        flags: int = 0,
    ) -> None:
        if self.responded:
            raise InteractionException('This interaction has already been responded to')

        await self._parent._state.http.create_interaction_response(
            self._parent.id,
            self._parent.token,
            {'type': 4, 'data': {'content': content, 'tts': tts, 'embeds': embeds, 'flags': flags}}
        )
        self.responded = True
        
