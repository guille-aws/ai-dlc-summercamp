"""Identity & Access helpers (US-12).

Extracts a Principal from an API Gateway event carrying Cognito authorizer
claims, and enforces role checks. Returns result tuples for authorization.
"""

from __future__ import annotations

from typing import Optional

from .errors import AuthorizationError, ValidationError
from .models import Principal
from .result import Result, err, ok

ROLE_SUBMITTER = "Submitter"
ROLE_REVIEWER = "Reviewer"
ROLE_SUPERVISOR = "Supervisor"


def principal_from_event(event: dict) -> Result:
    """Build a Principal from API Gateway Cognito authorizer claims.

    Returns (Principal, None) or (None, ValidationError).
    """
    try:
        claims = (
            event.get("requestContext", {})
            .get("authorizer", {})
            .get("claims", {})
        )
    except AttributeError:
        return err(ValidationError("Malformed request context"))

    if not claims:
        return err(ValidationError("No authorizer claims present"))

    user_id = claims.get("sub", "")
    email = claims.get("email", "")
    groups_raw = claims.get("cognito:groups", "")
    if isinstance(groups_raw, list):
        roles = groups_raw
    else:
        roles = [g for g in str(groups_raw).split(",") if g]

    if not user_id:
        return err(ValidationError("Missing subject in claims"))

    return ok(Principal(user_id=user_id, email=email, roles=roles))


def require_role(principal: Principal, role: str) -> Result:
    """Ensure the principal has the given role. Returns (principal, None) or error."""
    if role in principal.roles:
        return ok(principal)
    return err(
        AuthorizationError(f"Principal {principal.user_id} lacks required role: {role}")
    )


def require_any_role(principal: Principal, roles: list) -> Result:
    """Ensure the principal has at least one of the given roles."""
    if any(r in principal.roles for r in roles):
        return ok(principal)
    return err(
        AuthorizationError(
            f"Principal {principal.user_id} lacks any of roles: {', '.join(roles)}"
        )
    )
