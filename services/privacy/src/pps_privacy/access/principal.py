"""Who is making this request.

This is the handover point between authentication and the privacy layer.

**Hemanth's side owns authentication**: proving the caller is who they claim to
be, via a signed session token, an OIDC token, whatever it ends up being. The
output of that is a :class:`Principal`.

**This side owns scoping**: turning a Principal into a database session that can
only see the rows that principal is allowed to see.

The split exists so neither side has to trust the other's internals. Hemanth
does not need to know about row-level security policies; this module does not
need to know how a token is verified. The only thing that crosses the boundary
is a Principal, and the single rule attached to it is:

    A Principal may only be built from *verified* authentication.
    Never from a request header, a query parameter, a form field, a cookie the
    client can write, or anything else a caller chooses.

That rule is enforced here, not left to discipline -- see
:meth:`Principal.from_verified_auth`, which refuses to mint the privileged
``system`` actor no matter what string it is handed.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

__all__ = ["Role", "Principal", "PrincipalError"]


class PrincipalError(ValueError):
    """A Principal could not be constructed from the given inputs."""


class Role(str, Enum):
    """Actor roles.

    The first five match the ``users.role`` CHECK constraint in migration 0002
    exactly. If either side adds a role, both have to change together --
    a value the database rejects will fail at insert time, and a value the
    database accepts but this enum does not will fail here.
    """

    STUDENT = "student"
    TRAINER = "trainer"
    RECRUITER = "recruiter"
    ADMIN = "admin"
    DPO = "dpo"

    #: Background jobs only: the retention sweep, the deletion worker. This is
    #: the one role whose row-level security policy grants broad visibility, so
    #: it is deliberately unreachable from :meth:`Principal.from_verified_auth`.
    #: A request path must never be able to produce it, whatever the token says.
    SYSTEM = "system"


#: Roles a real human session may hold. ``SYSTEM`` is absent on purpose.
HUMAN_ROLES = frozenset(
    {Role.STUDENT, Role.TRAINER, Role.RECRUITER, Role.ADMIN, Role.DPO}
)


@dataclass(frozen=True)
class Principal:
    """An authenticated actor.

    Construct via :meth:`from_verified_auth` (for people) or :meth:`system`
    (for background workers). The plain constructor is available for tests, but
    the named constructors are what application code should use, because they
    carry the checks.
    """

    user_id: uuid.UUID | None
    role: Role

    def __post_init__(self) -> None:
        if self.role is Role.SYSTEM:
            if self.user_id is not None:
                raise PrincipalError("the system principal has no user_id")
        elif self.user_id is None:
            raise PrincipalError(f"role {self.role.value!r} requires a user_id")

    @classmethod
    def from_verified_auth(cls, user_id: str | uuid.UUID, role: str | Role) -> Principal:
        """Build a Principal from an authenticated session.

        Call this **after** the token or session has been verified, with the
        identity that verification produced -- not with values taken from the
        request.

        Refuses to produce the ``system`` role. If a token ever arrives claiming
        it, that is either a bug or an attack, and either way the request should
        fail rather than be granted the one role that can see everything.
        """
        try:
            resolved = Role(role.value if isinstance(role, Role) else str(role).strip().lower())
        except ValueError as exc:
            raise PrincipalError(f"unknown role: {role!r}") from exc

        if resolved not in HUMAN_ROLES:
            raise PrincipalError(
                f"role {resolved.value!r} cannot be granted to a request. "
                "The system role is reserved for background workers and must "
                "never be reachable from an authenticated request path."
            )

        if isinstance(user_id, uuid.UUID):
            resolved_id = user_id
        else:
            try:
                resolved_id = uuid.UUID(str(user_id))
            except (ValueError, AttributeError) as exc:
                # Identifiers are UUIDs because guessable ones (stu_014,
                # trn_007) turn any authentication weakness into trivial
                # impersonation of a specific person.
                raise PrincipalError(
                    f"user_id must be a UUID, got {user_id!r}"
                ) from exc

        return cls(user_id=resolved_id, role=resolved)

    @classmethod
    def system(cls) -> Principal:
        """The background-worker principal. Sees every row.

        Only for processes with no request path: the retention sweep, the
        deletion worker, migrations. If you are reaching for this inside code
        that serves a user, the answer is no -- that is the one shape that
        turns this whole scheme off.
        """
        return cls(user_id=None, role=Role.SYSTEM)

    @property
    def is_system(self) -> bool:
        return self.role is Role.SYSTEM

    def __repr__(self) -> str:
        # A user_id is a pseudonymous identifier rather than a direct one, but
        # it still ends up in logs, so keep it short rather than splattering a
        # full record into every trace line.
        who = "system" if self.is_system else str(self.user_id)
        return f"Principal({self.role.value}, {who})"
