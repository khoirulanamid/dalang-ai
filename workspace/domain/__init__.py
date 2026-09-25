"""
domain/__init__.py
==================
Dalang-AI Domain Package — Task T-801

Exposes the public surface of the domain layer following Domain-Driven Design
(DDD) principles.  All names use the project's ubiquitous language.

Sub-modules
-----------
value_objects  – Immutable, identity-less domain primitives.
user           – User aggregate root, UserInDB (persistence), UserPublic (DTO).
parsers        – Raw-dict → domain-object parsers with strict validation.
"""

from domain.value_objects import (
    EmailAddress,
    HashedPassword,
    Timestamp,
    UserId,
    Username,
)
from domain.user import (
    UserAggregate,
    UserInDB,
    UserPublic,
    UserRole,
)
from domain.parsers import (
    parse_registration_input,
    parse_user_from_db_record,
    parse_user_public_from_dict,
)

__all__ = [
    # Value Objects
    "EmailAddress",
    "HashedPassword",
    "Timestamp",
    "UserId",
    "Username",
    # Aggregate / DTOs
    "UserAggregate",
    "UserInDB",
    "UserPublic",
    "UserRole",
    # Parsers
    "parse_registration_input",
    "parse_user_from_db_record",
    "parse_user_public_from_dict",
]
