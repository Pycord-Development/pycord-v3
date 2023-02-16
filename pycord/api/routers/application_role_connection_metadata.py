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
from ...snowflake import Snowflake
from ...types import ApplicationRoleConnectionMetadata
from ..route import Route
from .base import BaseRouter


class ApplicationRoleConnections(BaseRouter):
    async def get_application_role_connection_metadata_records(
        self, application_id: Snowflake,
    ) -> list[ApplicationRoleConnectionMetadata]:
        return await self.request(
            'GET',
            Route(
                '/applications/{application_id}/role-connections/metadata', application_id=application_id,
            )
        )

    async def update_application_role_connection_metadata_records(
        self, application_id: Snowflake, records: list[ApplicationRoleConnectionMetadata],
    ) -> list[ApplicationRoleConnectionMetadata]:
        return self.request(
            'PUT',
            Route(
                '/applications/{application_id}/role-connections/metadata', application_id=application_id,
            ),
            records,
        )