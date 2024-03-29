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
from ...missing import MISSING, MissingEnum
from ...snowflake import Snowflake
from ...types import (
    CTYPE,
    Channel,
    DefaultReaction,
    FollowedChannel,
    ForumTag,
    ForumThreadMessageParams,
    Invite,
    ListThreadsResponse,
    Message,
    Overwrite,
    ThreadMember,
)
from ...utils import remove_undefined
from ..route import Route
from .base import BaseRouter


class Channels(BaseRouter):
    async def get_channel(
        self,
        channel_id: Snowflake,
    ) -> Channel:
        return await self.request(
            'GET', Route('/channels/{channel_id}', channel_id=channel_id)
        )

    async def modify_channel(
        self,
        channel_id: Snowflake,
        *,
        name: str | MissingEnum = MISSING,
        # Group DM Only
        icon: bytes | MissingEnum = MISSING,  # TODO
        # Thread Only
        archived: bool | MissingEnum = MISSING,
        auto_archive_duration: int | MissingEnum = MISSING,
        locked: bool | MissingEnum = MISSING,
        invitable: bool | MissingEnum = MISSING,
        applied_tags: list[Snowflake] | MissingEnum = MISSING,
        # Thread & Guild Channels
        rate_limit_per_user: int | None | MissingEnum = MISSING,
        flags: int | None | MissingEnum = MISSING,
        # Guild Channels Only
        type: CTYPE | MissingEnum = MISSING,
        position: int | None | MissingEnum = MISSING,
        topic: str | None | MissingEnum = MISSING,
        nsfw: bool | None | MissingEnum = MISSING,
        bitrate: int | None | MissingEnum = MISSING,
        user_imit: int | None | MissingEnum = MISSING,
        permission_overwrites: list[Overwrite] | None | MissingEnum = MISSING,
        parent_id: int | None | MissingEnum = MISSING,
        rtc_region: str | None | MissingEnum = MISSING,
        video_quality_mode: int | None | MissingEnum = MISSING,
        default_auto_archive_duration: int | None | MissingEnum = MISSING,
        available_tags: list[ForumTag] | None | MissingEnum = MISSING,
        default_reaction_emoji: DefaultReaction | None | MissingEnum = MISSING,
        default_thread_rate_limit_per_user: int | MissingEnum = MISSING,
        default_sort_order: int | None | MissingEnum = MISSING,
        default_forum_layout: int | MissingEnum = MISSING,
        # Reason
        reason: str | None = None,
    ) -> Channel:
        data = {
            'name': name,
            'archived': archived,
            'auto_archive_duration': auto_archive_duration,
            'locked': locked,
            'invitable': invitable,
            'applied_tags': applied_tags,
            'rate_limit_per_user': rate_limit_per_user,
            'flags': flags,
            'type': type,
            'position': position,
            'topic': topic,
            'nsfw': nsfw,
            'bitrate': bitrate,
            'user_limit': user_imit,
            'permission_overwrites': permission_overwrites,
            'parent_id': parent_id,
            'rtc_region': rtc_region,
            'video_quality_mode': video_quality_mode,
            'default_auto_archive_duration': default_auto_archive_duration,
            'available_tags': available_tags,
            'default_reaction_emoji': default_reaction_emoji,
            'default_thread_rate_limit_per_user': default_thread_rate_limit_per_user,
            'default_sort_order': default_sort_order,
            'default_forum_layout': default_forum_layout,
        }
        return await self.request(
            'PATCH',
            Route('/channels/{channel_id}', channel_id=channel_id),
            remove_undefined(**data),
            reason=reason,
        )

    async def delete_channel(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'DELETE',
            Route('/channels/{channel_id}', channel_id=channel_id),
            reason=reason,
        )

    async def edit_channel_permissions(
        self,
        channel_id: Snowflake,
        overwrite_id: Snowflake,
        *,
        type: int,
        allow: int | None | MissingEnum = MISSING,
        deny: int | None | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> None:
        data = {
            'allow': str(allow),
            'deny': str(deny),
            'type': type,
        }
        await self.request(
            'PUT',
            Route(
                '/channels/{channel_id}/permissions/{overwrite_id}',
                channel_id=channel_id,
                overwrite_id=overwrite_id,
            ),
            remove_undefined(**data),
            reason=reason,
        )

    async def get_channel_invites(
        self,
        channel_id: Snowflake,
    ) -> list[Invite]:
        return await self.request(
            'GET', Route('/channels/{channel_id}/invites', channel_id=channel_id)
        )

    async def create_channel_invite(
        self,
        channel_id: Snowflake,
        *,
        max_age: int | MissingEnum = MISSING,
        max_uses: int | MissingEnum = MISSING,
        temporary: bool | MissingEnum = MISSING,
        unique: bool | MissingEnum = MISSING,
        target_type: int | MissingEnum = MISSING,
        target_user_id: Snowflake | MissingEnum = MISSING,
        target_application_id: Snowflake | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> Invite:
        data = {
            'max_age': max_age,
            'max_uses': max_uses,
            'temporary': temporary,
            'unique': unique,
            'target_type': target_type,
            'target_user_id': target_user_id,
            'target_application_id': target_application_id,
        }
        return await self.request(
            'POST',
            Route('/channels/{channel_id}/invites', channel_id=channel_id),
            remove_undefined(**data),
            reason=reason,
        )

    async def delete_channel_permission(
        self,
        channel_id: Snowflake,
        overwrite_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/permissions/{overwrite_id}',
                channel_id=channel_id,
                overwrite_id=overwrite_id,
            ),
            reason=reason,
        )

    async def follow_announcement_channel(
        self,
        channel_id: Snowflake,
        *,
        webhook_channel_id: Snowflake,
    ) -> FollowedChannel:
        data = {
            'webhook_channel_id': webhook_channel_id,
        }
        return await self.request(
            'POST',
            Route(
                '/channels/{channel_id}/followers',
                channel_id=channel_id,
            ),
            data,
        )

    async def trigger_typing_indicator(
        self,
        channel_id: Snowflake,
    ) -> None:
        await self.request(
            'POST', Route('/channels/{channel_id}/typing', channel_id=channel_id)
        )

    async def get_pinned_messages(
        self,
        channel_id: Snowflake,
    ) -> list[Message]:
        return await self.request(
            'GET', Route('/channels/{channel_id}/pins', channel_id=channel_id)
        )

    async def group_dm_add_recipient(
        self,
        channel_id: Snowflake,
        user_id: Snowflake,
        *,
        access_token: str,
        nick: str | None | MissingEnum = MISSING,
    ) -> None:
        data = {
            'access_token': access_token,
            'nick': nick,
        }
        await self.request(
            'PUT',
            Route(
                '/channels/{channel_id}/recipients/{user_id}',
                channel_id=channel_id,
                user_id=user_id,
            ),
            data,
        )

    async def group_dm_remove_recipient(
        self,
        channel_id: Snowflake,
        user_id: Snowflake,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/recipients/{user_id}',
                channel_id=channel_id,
                user_id=user_id,
            ),
        )

    async def start_thread_from_message(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        name: str,
        auto_archive_duration: int | MissingEnum = MISSING,
        rate_limit_per_user: int | None | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> Channel:
        data = {
            'name': name,
            'auto_archive_duration': auto_archive_duration,
            'rate_limit_per_user': rate_limit_per_user,
        }
        return await self.request(
            'POST',
            Route(
                '/channels/{channel_id}/messages/{message_id}/threads',
                channel_id=channel_id,
                message_id=message_id,
            ),
            remove_undefined(**data),
            reason=reason,
        )

    async def start_thread_without_message(
        self,
        channel_id: Snowflake,
        *,
        name: str,
        auto_archive_duration: int | MissingEnum = MISSING,
        type: CTYPE | MissingEnum = MISSING,
        invitable: bool | MissingEnum = MISSING,
        rate_limit_per_user: int | None | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> Channel:
        data = {
            'name': name,
            'auto_archive_duration': auto_archive_duration,
            'type': type,
            'invitable': invitable,
            'rate_limit_per_user': rate_limit_per_user,
        }
        return await self.request(
            'POST',
            Route(
                '/channels/{channel_id}/threads',
                channel_id=channel_id,
            ),
            remove_undefined(**data),
            reason=reason,
        )

    async def start_thread_in_forum_channel(
        self,
        channel_id: Snowflake,
        *,
        name: str,
        auto_archive_duration: int | MissingEnum = MISSING,
        rate_limit_per_user: int | None | MissingEnum = MISSING,
        message: ForumThreadMessageParams,
        applied_tags: list[Snowflake] | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> Channel:
        data = {
            'name': name,
            'auto_archive_duration': auto_archive_duration,
            'rate_limit_per_user': rate_limit_per_user,
        }
        return await self.request(
            'POST',
            Route(
                '/channels/{channel_id}/threads',
                channel_id=channel_id,
            ),
            remove_undefined(**data),
            reason=reason,
        )

    async def join_thread(
        self,
        channel_id: Snowflake,
    ) -> None:
        await self.request(
            'PUT',
            Route(
                '/channels/{channel_id}/thread-members/@me',
                channel_id=channel_id,
            ),
        )

    async def add_thread_member(
        self,
        channel_id: Snowflake,
        user_id: Snowflake,
    ) -> None:
        await self.request(
            'PUT',
            Route(
                '/channels/{channel_id}/thread-members/{user_id}',
                channel_id=channel_id,
                user_id=user_id,
            ),
        )

    async def leave_thread(
        self,
        channel_id: Snowflake,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/thread-members/@me',
                channel_id=channel_id,
            ),
        )

    async def remove_thread_member(
        self,
        channel_id: Snowflake,
        user_id: Snowflake,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/thread-members/{user_id}',
                channel_id=channel_id,
                user_id=user_id,
            ),
        )

    async def get_thread_member(
        self,
        channel_id: Snowflake,
        user_id: Snowflake,
        *,
        with_member: bool | MissingEnum = MISSING,
    ) -> ThreadMember:
        params = {
            'with_member': with_member,
        }
        return await self.request(
            'GET',
            Route(
                '/channels/{channel_id}/thread-members/{user_id}',
                channel_id=channel_id,
                user_id=user_id,
            ),
            params=remove_undefined(params),
        )

    async def list_thread_members(
        self,
        channel_id: Snowflake,
        *,
        with_member: bool | MissingEnum = MISSING,
        after: Snowflake | MissingEnum = MISSING,
        limit: int | MissingEnum = MISSING,
    ) -> list[ThreadMember]:
        params = {
            'with_member': with_member,
            'after': after,
            'limit': limit,
        }
        return await self.request(
            'GET',
            Route(
                '/channels/{channel_id}/thread-members',
                channel_id=channel_id,
            ),
            params=remove_undefined(params),
        )

    async def list_public_archived_threads(
        self,
        channel_id: Snowflake,
        *,
        before: str | MissingEnum = MISSING,
        limit: int | MissingEnum = MISSING,
    ) -> ListThreadsResponse:
        params = {
            'before': before,
            'limit': limit,
        }
        return await self.request(
            'GET',
            Route(
                '/channels/{channel_id}/threads/archived/public',
                channel_id=channel_id,
            ),
            params=remove_undefined(params),
        )

    async def list_private_archived_threads(
        self,
        channel_id: Snowflake,
        *,
        before: str | MissingEnum = MISSING,
        limit: int | MissingEnum = MISSING,
    ) -> ListThreadsResponse:
        params = {
            'before': before,
            'limit': limit,
        }
        return await self.request(
            'GET',
            Route(
                '/channels/{channel_id}/threads/archived/private',
                channel_id=channel_id,
            ),
            params=remove_undefined(params),
        )

    async def list_joined_private_archived_threads(
        self,
        channel_id: Snowflake,
        *,
        before: str | MissingEnum = MISSING,
        limit: int | MissingEnum = MISSING,
    ) -> ListThreadsResponse:
        params = {
            'before': before,
            'limit': limit,
        }
        return await self.request(
            'GET',
            Route(
                '/channels/{channel_id}/users/@me/threads/archived/private',
                channel_id=channel_id,
            ),
            params=remove_undefined(params),
        )
