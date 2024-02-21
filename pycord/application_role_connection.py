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

from __future__ import annotations

from .enums import ApplicationRoleConnectionMetadataType
from .missing import Maybe, MISSING

from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import ApplicationRoleConnectionMetadataData, Locales

__all__ = (
    "ApplicationRoleConnectionMetadata",
)


class ApplicationRoleConnectionMetadata:
    __slots__ = (
        "type",
        "key",
        "name",
        "description",
        "name_localizations",
        "description_localizations",
    )

    def __init__(
        self,
        type: ApplicationRoleConnectionMetadataType,
        *,
        key: str,
        name: str,
        description: str,
        name_localizations: Maybe[dict[Locales, str]] = MISSING,
        description_localizations: Maybe[dict[Locales, str]] = MISSING,
    ) -> None:
        self.type: ApplicationRoleConnectionMetadataType = type
        self.key: str = key
        self.name: str = name
        self.description: str = description
        self.name_localizations: Maybe[dict[Locales, str]] = name_localizations
        self.description_localizations: Maybe[dict[Locales, str]] = description_localizations

    def __repr__(self) -> str:
        return f"<ApplicationRoleConnectionMetadata type={self.type} key={self.key!r}>"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_data(cls, data: ApplicationRoleConnectionMetadataData) -> ApplicationRoleConnectionMetadata:
        return cls(
            ApplicationRoleConnectionMetadataType(data["type"]),
            key=data["key"],
            name=data["name"],
            description=data["description"],
            name_localizations=data.get("name_localizations", MISSING),
            description_localizations=data.get("description_localizations", MISSING),
        )

    def to_data(self) -> ApplicationRoleConnectionMetadataData:
        payload: ApplicationRoleConnectionMetadataData = {
            "type": self.type.value,
            "key": self.key,
            "name": self.name,
            "description": self.description,
        }
        if self.name_localizations is not MISSING:
            payload["name_localizations"] = cast(dict[Locales, str], self.name_localizations)
        if self.description_localizations is not MISSING:
            payload["description_localizations"] = cast(dict[Locales, str], self.description_localizations)
        return payload
