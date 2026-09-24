"""Turn a :class:`~.principal.Principal` into a database session that can only
see what that principal is allowed to see.

How it works: the row-level security policies in migration 0004 read three
PostgreSQL session settings -- ``app.actor_role``, ``app.actor_id`` and, for
trainers, ``app.trainer_batches``. This module sets them, correctly and
transaction-locally, so callers never write the SQL themselves.

Two design points worth knowing before changing anything here.

**Settings are transaction-scoped.** They are applied with ``set_config(..., true)``,
which is ``SET LOCAL``: they vanish when the transaction ends. That matters
because connections are pooled. A setting that outlived its transaction would
leak one user's scope into the next request that borrowed the same connection,
which is the worst bug this whole design could have.

**Values are passed as parameters, never interpolated.** ``SET LOCAL`` cannot
take parameters, which tempts people into f-strings; ``set_config()`` is a
normal function call and can, so that is what we use. Building this SQL by
string formatting would put a caller-influenced value straight into a statement
that decides authorisation.

**The zone boundary is explicit here.** The analysis database role cannot read
the identity schema -- that is the point of the split -- so it cannot look up
which batches a trainer teaches. Instead the caller resolves scope on an
identity connection with :func:`resolve_scope`, then applies it to an analysis
connection. The crossing is a deliberate two-step, visible in the call site,
rather than a join the database quietly permits.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Protocol

from .principal import Principal, Role

__all__ = ["Scope", "resolve_scope", "scoped_session", "apply_context"]


class _Connection(Protocol):  # pragma: no cover - structural type
    def execute(self, query: str, params: Any = ...) -> Any: ...
    def transaction(self) -> Any: ...


@dataclass(frozen=True)
class Scope:
    """Scope facts that live in the identity zone.

    Resolved once per request on an identity connection, then handed to
    whichever connection needs it.
    """

    #: The principal's pseudonymous ID, used to scope analysis-zone queries.
    candidate_pid: uuid.UUID | None = None
    #: Batches this trainer is *currently* assigned to. Empty for everyone else.
    trainer_batches: tuple[uuid.UUID, ...] = field(default=())


def resolve_scope(identity_conn: _Connection, principal: Principal) -> Scope:
    """Look up the scope facts for ``principal``. Requires an identity connection.

    For a trainer this reads ``identity.trainer_assignments`` and keeps only
    assignments with no ``revoked_at`` -- so access ends when the assignment
    does, including for batches they used to teach.
    """
    if principal.is_system:
        return Scope()

    candidate_pid = None
    row = identity_conn.execute(
        "SELECT candidate_pid FROM identity.users WHERE user_id = %s",
        (principal.user_id,),
    ).fetchone()
    if row is not None:
        candidate_pid = row[0]

    batches: tuple[uuid.UUID, ...] = ()
    if principal.role is Role.TRAINER:
        rows = identity_conn.execute(
            "SELECT batch_id FROM identity.trainer_assignments "
            "WHERE trainer_id = %s AND revoked_at IS NULL",
            (principal.user_id,),
        ).fetchall()
        batches = tuple(r[0] for r in rows)

    return Scope(candidate_pid=candidate_pid, trainer_batches=batches)


def apply_context(conn: _Connection, principal: Principal, scope: Scope | None = None) -> None:
    """Set the session settings the RLS policies read.

    Must run inside a transaction. :func:`scoped_session` is the normal way in;
    call this directly only when you are already managing the transaction.
    """
    scope = scope or Scope()

    conn.execute("SELECT set_config('app.actor_role', %s, true)", (principal.role.value,))
    conn.execute(
        "SELECT set_config('app.actor_id', %s, true)",
        ("" if principal.user_id is None else str(principal.user_id),),
    )
    conn.execute(
        "SELECT set_config('app.candidate_pid', %s, true)",
        ("" if scope.candidate_pid is None else str(scope.candidate_pid),),
    )
    # Comma-separated because a session setting is text. The policy parses it
    # with string_to_array(...)::uuid[], so a malformed value raises rather than
    # silently widening the scope.
    conn.execute(
        "SELECT set_config('app.trainer_batches', %s, true)",
        (",".join(str(b) for b in scope.trainer_batches),),
    )


@contextmanager
def scoped_session(
    conn: _Connection, principal: Principal, scope: Scope | None = None
) -> Iterator[_Connection]:
    """Run a block with the connection scoped to ``principal``.

    Every query inside is filtered by the row-level security policies::

        with scoped_session(conn, principal, scope) as session:
            rows = session.execute("SELECT user_id FROM identity.users").fetchall()

    That query returns the principal's own row, or their batch's students if
    they are an assigned trainer, or nothing at all -- without the caller
    writing a single WHERE clause. A caller who forgets to filter gets no rows
    rather than everyone's.

    Passing no ``scope`` is safe but restrictive: a trainer with no resolved
    batches sees nothing. Failing closed is the intended behaviour.
    """
    with conn.transaction():
        apply_context(conn, principal, scope)
        yield conn
