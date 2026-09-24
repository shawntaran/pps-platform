"""The seam between authentication and the privacy layer.

Authentication proves who the caller is and produces a :class:`Principal`.
This package turns that Principal into a database session scoped to exactly
what they may see. Neither side needs to know how the other works.

    from pps_privacy.access import Principal, resolve_scope, scoped_session

    principal = Principal.from_verified_auth(user_id, role)   # after auth
    scope = resolve_scope(identity_conn, principal)

    with scoped_session(identity_conn, principal, scope) as session:
        rows = session.execute("SELECT user_id FROM identity.users").fetchall()

The one rule that crosses the boundary: a Principal may only be built from
verified authentication, never from anything a caller supplies. The integration
contract is in docs/privacy/integration-contract.md.
"""

from .principal import HUMAN_ROLES, Principal, PrincipalError, Role
from .session import Scope, apply_context, resolve_scope, scoped_session

__all__ = [
    "HUMAN_ROLES",
    "Principal",
    "PrincipalError",
    "Role",
    "Scope",
    "apply_context",
    "resolve_scope",
    "scoped_session",
]
