from typing import Dict, Any
from fastapi import Header, HTTPException, status
from api_server.database import USERS, ROLE_PERMISSIONS

def authenticate_user(account_key: str, claimed_role: str) -> Dict[str, Any]:
    """
    Authenticate demo user credentials against mock user store
    and strictly verify role consistency.
    """
    user = USERS.get(account_key.lower().strip())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No demo account registered for key '{account_key}'."
        )

    if user["role"] != claimed_role.lower().strip():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Account '{user['name']}' is registered as '{user['role']}', not '{claimed_role}'."
        )

    return user

def require_auth(
    x_user_id: str = Header(..., description="Authenticated User ID"),
    x_user_role: str = Header(..., description="Claimed User Role")
) -> Dict[str, Any]:
    """
    Dependency to verify incoming request headers against registered users.
    """
    # Find user by ID
    user = None
    for u in USERS.values():
        if u["id"] == x_user_id:
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication credentials."
        )

    if user["role"] != x_user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Security Violation: Token role '{user['role']}' does not match header role '{x_user_role}'."
        )

    return user

def require_permission(permission: str):
    """
    Dependency factory to enforce specific RBAC permissions.
    """
    def permission_checker(
        x_user_id: str = Header(...),
        x_user_role: str = Header(...)
    ) -> Dict[str, Any]:
        user = require_auth(x_user_id, x_user_role)
        allowed_perms = ROLE_PERMISSIONS.get(user["role"], set())
        
        if permission not in allowed_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Role '{user['role']}' lacks permission '{permission}'."
            )
        return user

    return permission_checker
