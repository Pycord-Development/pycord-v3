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

import asyncio
from copy import copy
from inspect import isclass
from typing import TYPE_CHECKING, Any, Sequence, Union, get_origin

from ...channel import Channel, identify_channel
from ...enums import ApplicationCommandOptionType, ApplicationCommandType
from ...events.other import InteractionCreate
from ...interaction import Interaction, InteractionOption
from ...media import Attachment
from ...member import Member
from ...message import Message
from ...missing import MISSING, Maybe, MissingEnum
from ...role import Role
from ...snowflake import Snowflake
from ...types import AsyncFunc
from ...types.interaction import ApplicationCommandData
from ...user import User
from ...utils import get_arg_defaults, get_args, remove_undefined
from ..command import Command
from ..group import Group
from .context import Context
from .errors import ApplicationCommandException

if TYPE_CHECKING:
    from ...state import State

__all__: Sequence[str] = ('CommandChoice', 'Option', 'ApplicationCommand')


async def _autocomplete(
    _: Interaction, option: Option, string: str
) -> list[dict[str, Any]]:
    string = str(string).lower()
    return [
        choice._to_dict()
        for choice in option._choices
        if string in str(choice.value).lower()
    ]


class CommandChoice:
    """
    A single choice of an option. Used often in autocomplete-based commands

    Parameters
    ----------
    name: :class:`str`
        The name of this choice
    value: :class:`str` | :class:`int` :class:`float`
        The value of this choice
    name_localizations: dict[:class:`str`, :class:`str`]
        Dictionary of localizations
    """

    def __init__(
        self,
        name: str,
        name_localizations: dict[str, str] | None = None,
        value: str | int | float | None = None,
    ) -> None:
        self.name = name

        if value is None:
            self.value = name

        self.name_localizations = name_localizations

    def _to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'name_localizations': self.name_localizations,
        }


_OPTION_BIND = {
    str: ApplicationCommandOptionType.STRING,
    int: ApplicationCommandOptionType.INTEGER,
    bool: ApplicationCommandOptionType.BOOLEAN,
    float: ApplicationCommandOptionType.NUMBER,
    User: ApplicationCommandOptionType.USER,
    Channel: ApplicationCommandOptionType.CHANNEL,
    Role: ApplicationCommandOptionType.ROLE,
    Attachment: ApplicationCommandOptionType.ATTACHMENT,
}


class Option:
    """
    An option of a Chat Input Command.

    Parameters
    ----------
    type: :class:`.ApplicationCommandOptionType` | :class:`int`
        The type of Option
    name: :class:`str`
        The name of this Option
    description: :class:`str`
        The description of what and why this option is needed
    name_localizations: dict[:class:`str`, :class:`str`]
        Dictionary of localizations
    description_localizations: dict[:class:`str`, :class:`str`]
        Dictionary of localizations
    required: bool
        Is this option required to pass
        Defaults to False.
    choices: list[:class:`.CommandChoice`]
        The choices this option can be given. Often used in autocomplete
    options: list[:class:`Option`]
        Extra Options to add. ONLY support for Sub Commands
    channel_types: list[:class:`int`]
        A list of channel types to keep lock of
    min_value: :class:`int`
        The minimum integer value
    max_value: :class:`int`
        The maximum integer value
    autocomplete: :class:`bool`
        Whether to implement autocomplete or not
    """

    _level: int = 0

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        type: ApplicationCommandOptionType
        | int
        | Any = ApplicationCommandOptionType.STRING,
        name_localizations: dict[str, str] | MissingEnum = MISSING,
        description_localizations: dict[str, str] | MissingEnum = MISSING,
        required: bool | MissingEnum = MISSING,
        choices: list[CommandChoice] | MissingEnum = MISSING,
        options: list['Option'] | MissingEnum = MISSING,
        channel_types: list[int] | MissingEnum = MISSING,
        min_value: int | MissingEnum = MISSING,
        max_value: int | MissingEnum = MISSING,
        autocomplete: bool | MissingEnum = MISSING,
        autocompleter: AsyncFunc = _autocomplete,
    ) -> None:
        if isinstance(type, ApplicationCommandOptionType):
            self.type = type.value
        elif not isinstance(type, int):
            self.type = _OPTION_BIND[type].value
        else:
            self.type = type
        self.autocompleter = autocompleter
        self.name = name
        self.name_localizations = name_localizations
        self.description = description or 'No description provided'
        self.description_localizations = description_localizations
        self.required = required
        if autocomplete:
            self.choices = []
            if choices:
                self._choices = [choice for choice in choices if choices]
            else:
                self._choices = []
        else:
            if choices:
                self.choices = [choice._to_dict() for choice in choices]
            else:
                self.choices = MISSING
        if options is MISSING:
            self.options = []
        else:
            self.options = options
        self.channel_types = channel_types
        self.min_value = min_value
        self.max_value = max_value
        self.autocomplete = autocomplete
        self._subs = {}

        if TYPE_CHECKING:
            self.focused: bool | MissingEnum = MISSING
            self.value: str | int | float | MissingEnum = MISSING
            self.options: list[InteractionOption] = MISSING
            self._param: str = MISSING
            self._callback: AsyncFunc | None = MISSING

    @property
    def callback(self) -> AsyncFunc:
        return self._callback

    @callback.setter
    def callback(self, call: AsyncFunc | None) -> None:
        if call is None:
            self._callback = None
            return

        arg_defaults = get_arg_defaults(self._callback)
        self.options: list[Option] = []

        i: int = 0

        for name, v in arg_defaults.items():
            # ignore interaction
            if i == 0:
                i += 1
                continue

            if v[0] is None and name != 'self':
                raise ApplicationCommandException(
                    f'Parameter {name} on sub command {self.name} has no default set'
                )
            elif name == 'self':
                continue
            elif not isinstance(v[0], Option):
                raise ApplicationCommandException(
                    f'Options may only be of type Option, not {v[0]}'
                )

            v[0]._param = name

            self.options.append(v[0])

    def __get__(self):
        return self.value

    def _inter_copy(self, data: InteractionOption) -> Option:
        c = copy(self)

        c.focused = data.focused
        c.value = data.value
        c.options = data.options
        return c

    def to_dict(self) -> dict[str, Any]:
        return remove_undefined(
            type=self.type,
            name=self.name,
            name_localizations=self.name_localizations,
            description=self.description,
            description_localizations=self.description_localizations,
            required=self.required,
            choices=self.choices,
            options=[option.to_dict() for option in self.options]
            if self.options is not MISSING
            else MISSING,
            channel_types=self.channel_types,
            min_value=self.min_value,
            max_value=self.max_value,
            autocomplete=self.autocomplete,
        )

    def command(
        self,
        name: str | None = None,
        description: str | None = None,
        name_localizations: dict[str, str] | MissingEnum = MISSING,
        description_localizations: dict[str, str] | MissingEnum = MISSING,
    ) -> ApplicationCommand:
        """
        Add a command to this sub command to make it a group.

        Parameters
        ----------
        name: :class:`str`
            The name of this newly instantiated sub command
        description: :class:`str`
            The description of this newly created sub command
        name_localizations: dict[:class:`str`, :class:`str`]
            Dictionary of localizations
        description_localizations: dict[:class:`str`, :class:`str`]
            Dictionary of localizations
        """

        def wrapper(func: AsyncFunc):
            command = Option(
                type=1,
                name=name or func.__name__.lower(),
                description=description or func.__doc__ or 'No description provided',
                name_localizations=name_localizations,
                description_localizations=description_localizations,
            )
            command._callback = func

            if self._level == 2:
                raise ApplicationCommandException(
                    'Sub commands cannot be three levels deep'
                )

            command._level = self._level + 1

            if self._subs == {}:
                self.options = []
                self._callback = None

            self.options.append(command)

            self._subs[name] = command

            if self.type == 1:
                # turn into a command group
                self.type = 2

            return command

        return wrapper


class ApplicationCommand(Command):
    """
    Commands deployed to Discord by Applications

    Parameters
    ----------
    name: :class:`str`
        The name of this Command
    type: :class:`ApplicationCommandType`
        The type of Application Command
    description: :class:`str`
        The description for this command
    guild_id: :class:`int`
        The Guild ID to limit this command to.
        Defaults to None.
    name_localizations: dict[:class:`str`, :class:`str`]
        Dictionary of localizations
    description_localizations: dict[:class:`str`, :class:`str`]
        Dictionary of localizations
    dm_permission: :class:`bool`
        If this command should be instantiatable in DMs
        Defaults to True.
    nsfw: :class:`bool`
        Whether this Application Command is for NSFW audiences or not
        Defaults to False.
    default_member_permissions: :class:`int`
        The default member permissions for this command.
    """

    _processor_event = InteractionCreate(Context)
    sub_level: int = 0

    def __init__(
        self,
        # normal parameters
        callback: AsyncFunc | None,
        state: State,
        name: str | MissingEnum = MISSING,
        type: int | ApplicationCommandType = ApplicationCommandType.CHAT_INPUT,
        description: str | MissingEnum = MISSING,
        guild_id: int | None = None,
        group: Group | None = None,
        # discord parameters
        name_localizations: dict[str, str] | MissingEnum = MISSING,
        description_localizations: dict[str, str] | MissingEnum = MISSING,
        dm_permission: bool | MissingEnum = MISSING,
        nsfw: bool | MissingEnum = MISSING,
        default_member_permissions: Maybe[int] = MISSING,
    ) -> None:
        super().__init__(callback, name, state, group)

        self.name = name or callback.__name__.lower()

        if isinstance(type, ApplicationCommandType):
            self.type = type.value
        else:
            self.type = type

        self.guild_id = guild_id
        self.name_localizations = name_localizations
        if self.type == ApplicationCommandType.CHAT_INPUT.value:
            self.description = (
                description or callback.__doc__ or 'No description provided'
            )
        else:
            self.description = MISSING
        self.description_localizations = description_localizations
        self.dm_permission = dm_permission
        self.nsfw = nsfw
        self._options = []
        self._parse_arguments()
        if self.type == 1:
            self._subs: dict[str, ApplicationCommand] = {}
        self._created: bool = False
        self.default_member_permissions = default_member_permissions

    def command(
        self,
        name: str | MissingEnum = MISSING,
        description: str | MissingEnum = MISSING,
        name_localizations: dict[str, str] | MissingEnum = MISSING,
        description_localizations: dict[str, str] | MissingEnum = MISSING,
    ) -> ApplicationCommand:
        """
        Add a sub command to this command

        Parameters
        ----------
        name: :class:`str`
            The name of this newly instantiated sub command
        description: :class:`str`
            The description of this newly created sub command
        name_localizations: dict[:class:`str`, :class:`str`]
            Dictionary of localizations
        description_localizations: dict[:class:`str`, :class:`str`]
            Dictionary of localizations
        """

        def wrapper(func: AsyncFunc):
            if self.type != 1:
                raise ApplicationCommandException(
                    'Sub Commands cannot be created on non-slash-commands'
                )

            command = Option(
                type=1,
                name=name or func.__name__.lower(),
                description=description or func.__doc__ or 'No description provided',
                name_localizations=name_localizations,
                description_localizations=description_localizations,
            )
            command._callback = func
            command._level = 1

            if self._subs == {}:
                self.options = []
                self._options_dict = {}
                self._options = []
                self._callback = None

            self.options.append(command)
            self._options_dict[name] = command
            self._options.append(command.to_dict())

            self._subs[name] = command
            return command

        return wrapper

    def _parse_user_command_arguments(self) -> None:
        arg_defaults = get_arg_defaults(self._callback)

        fielded: bool = False
        i: int = 0

        for name, arg in arg_defaults.items():
            if i == 2:
                raise ApplicationCommandException(
                    'User Command has too many arguments, only one is allowed'
                )

            i += 1

            if (
                arg[1] != Member
                and arg[1] != User
                and arg[1] != Interaction
                and arg[1] != Union[User, Member]
            ):
                raise ApplicationCommandException(
                    'Command argument incorrectly type hinted'
                )

            fielded = True

            self._user_command_field = name

        if not fielded:
            raise ApplicationCommandException('No argument set for a member/user')

    def _parse_message_command_arguments(self) -> None:
        arg_defaults = get_arg_defaults(self._callback)

        fielded: bool = False
        i: int = 0

        for _, arg in arg_defaults.items():
            if i == 3:
                raise ApplicationCommandException(
                    'Message Command has too many arguments, only two are allowed'
                )

            i += 1

            if (
                arg[1] != Message
                and arg[1] != Interaction
                and arg[1] != User
                and arg[1] != Member
                and arg[1] != Union[User, Member]
            ):
                raise ApplicationCommandException(
                    'Command argument incorrectly type hinted'
                )

            if arg[1] != Interaction:
                fielded = True

        if not fielded:
            raise ApplicationCommandException('No argument set for a message and user')

    def _parse_arguments(self) -> None:
        if self.type == 2:
            self._parse_user_command_arguments()
            return
        elif self.type == 3:
            self._parse_message_command_arguments()
            return

        arg_defaults = get_arg_defaults(self._callback)
        self.options: list[Option] = []
        self._options_dict: dict[str, Option] = {}

        for name, v in arg_defaults.items():
            if name == 'self':
                continue
            elif v[1] is Interaction or v[1] is Context:
                continue

            args = get_args(v[1])

            if not isinstance(args[1], Option):
                raise ApplicationCommandException(
                    f'Options may only be of type Option, not {args[1]}'
                )

            option: Option = args[1]

            option._param = name
            option.type = _OPTION_BIND[args[0]].value

            if not option.name:
                option.name = name

            self.options.append(option)
            self._options_dict[option.name] = option

        for option in self.options:
            self._options.append(option.to_dict())

    async def instantiate(self) -> None:
        if self.guild_id:
            guild_commands: list[
                ApplicationCommandData
            ] = await self._state.http.get_guild_application_commands(
                self._state.user.id, self.guild_id, True
            )

            for app_cmd in guild_commands:
                if app_cmd['name'] not in self._state._application_command_names:
                    await self._state.http.delete_guild_application_command(
                        self._state.user.id, self.guild_id, app_cmd['id']
                    )
                    continue

                if app_cmd['name'] == self.name and self._state.update_commands:
                    if app_cmd['type'] != self.type:
                        continue

                    if self._created is True:
                        await self._state.http.delete_guild_application_command(
                            self._state.user.id, self.guild_id, app_cmd['id']
                        )
                        continue

                    self.id = app_cmd['id']

                    await self._state.http.edit_guild_application_command(
                        self._state.user.id,
                        Snowflake(app_cmd['id']),
                        guild_id=self.guild_id,
                        name=self.name,
                        name_localizations=self.name_localizations,
                        description=self.description,
                        description_localizations=self.description_localizations,
                        type=self.type,
                        options=self._options,
                    )
                    self._created = True

            if not self._created:
                res = await self._state.http.create_guild_application_command(
                    self._state.user.id,
                    guild_id=self.guild_id,
                    name=self.name,
                    name_localizations=self.name_localizations,
                    description=self.description,
                    description_localizations=self.description_localizations,
                    type=self.type,
                    options=self._options,
                )
                self.id = res['id']

            return

        for app_cmd in self._state.application_commands:
            if app_cmd['name'] == self.name and self._state.update_commands:
                if app_cmd['type'] != self.type:
                    continue

                if self._created is True:
                    await self._state.http.delete_global_application_command(
                        self._state.user.id, app_cmd['id']
                    )

                await self._state.http.edit_global_application_command(
                    self._state.user.id,
                    Snowflake(app_cmd['id']),
                    name=self.name,
                    name_localizations=self.name_localizations,
                    description=self.description,
                    description_localizations=self.description_localizations,
                    type=self.type,
                    options=self._options,
                )
                self._created = True
                self.id = app_cmd['id']

        if not self._created:
            res = await self._state.http.create_global_application_command(
                self._state.user.id,
                name=self.name,
                name_localizations=self.name_localizations,
                description=self.description,
                description_localizations=self.description_localizations,
                type=self.type,
                options=self._options,
            )
            self.id = res['id']

    async def _process_options(
        self,
        interaction: Interaction,
        options: list[InteractionOption],
        grouped: bool = False,
    ) -> dict[str, Any]:
        binding = {}
        for option in options:
            o = self._options_dict[option.name]
            if option.type == 1:
                sub = self._subs[option.name]

                opts = await self._process_options(
                    interaction=interaction, options=option.options
                )
                if not grouped:
                    await self._callback(interaction)
                await sub._callback(interaction, **opts)
            elif option.type == 2:
                await self._callback(interaction)
                await self._process_options(
                    interaction=interaction, options=option.options, grouped=True
                )
            elif option.type in (3, 4, 5, 10):
                binding[o._param] = o._inter_copy(option).value
            elif option.type == 6:
                user = User(
                    interaction.data['resolved']['users'][option.value], self._state
                )

                if interaction.guild_id:
                    member = Member(
                        interaction.data['resolved']['members'][option.value],
                        self._state,
                        guild_id=interaction.guild_id,
                    )
                    member.user = user

                    binding[o._param] = member
                else:
                    binding[o._param] = user
            elif option.type == 7:
                binding[o._param] = identify_channel(
                    interaction.data['resolved']['channels'][option.value], self._state
                )
            elif option.type == 8:
                binding[o._param] = Role(
                    interaction.data['resolved']['roles'][option.value], self._state
                )
            elif option.type == 9:
                if interaction.data['resolved'].get('roles'):
                    binding[o._param] = Role(
                        interaction.data['resolved']['roles'][option.value], self._state
                    )
                else:
                    user = User(
                        interaction.data['resolved']['users'][option.value], self._state
                    )

                    if interaction.guild_id:
                        member = Member(
                            interaction.data['resolved']['members'][option.value],
                            self._state,
                        )
                        member.user = user

                        binding[o._param] = member
                    else:
                        binding[o._param] = user
            elif option.type == 11:
                binding[o._param] = Attachment(
                    interaction.data['resolved']['attachments'][option.value],
                    self._state,
                )

        return binding

    def _process_user_command(self, inter: Interaction) -> User | Member:
        if inter.member:
            return inter.member
        else:
            return inter.user

    async def _invoke(self, event: InteractionCreate | Interaction) -> None:
        if not isinstance(event, Interaction):
            interaction = event.interaction
        else:
            interaction = event

        if interaction.type == 4:
            if interaction.data.get('name') is not None:
                if interaction.data['name'] == self.name:
                    option = interaction.data['options'][0]
                    real_option = self._options_dict[option['name']]
                    choices = await real_option.autocompleter(
                        interaction, real_option, option['value']
                    )

                    await interaction.response.autocomplete(choices)
            return

        if interaction.data:
            if interaction.data.get('name') is not None:
                if interaction.data['name'] == self.name:
                    if interaction.data['type'] == 1:
                        binding = await self._process_options(
                            interaction, interaction.options
                        )

                        if self._callback:
                            await self._callback(interaction, **binding)
                    elif interaction.data['type'] == 2:
                        user_binding = self._process_user_command(interaction)

                        await self._callback(interaction, user_binding)
                    elif interaction.data['type'] == 3:
                        message = Message(
                            interaction.data['resolved']['messages'][
                                interaction.data['target_id']
                            ],
                            self._state,
                        )
                        requester = self._process_user_command(interaction)

                        await self._callback(interaction, message, requester)
