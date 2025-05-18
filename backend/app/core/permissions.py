"""Role-Based Access Control (RBAC) utilities."""
from functools import wraps
from fastapi import HTTPException, status
from typing import List
from app.db.models import UserRole

class Permission:
    """Permission definitions for RBAC."""
    # Designed this after looking at how GitHub does their permissions
    # Kept it simple - we can always add more granular perms later
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    DELETE_LOGS = "delete_logs"
    EXPORT_DATA = "export_data"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    
    # User permissions
    CREATE_ALERTS = "create_alerts"
    UPDATE_ALERTS = "update_alerts"
    VIEW_ALERTS = "view_alerts"
    CREATE_LOGS = "create_logs"
    VIEW_LOGS = "view_logs"
    
    # Viewer permissions
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_ANALYTICS = "view_analytics"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.DELETE_LOGS,
        Permission.EXPORT_DATA,
        Permission.VIEW_AUDIT_LOGS,
        Permission.CREATE_ALERTS,
        Permission.UPDATE_ALERTS,
        Permission.VIEW_ALERTS,
        Permission.CREATE_LOGS,
        Permission.VIEW_LOGS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ANALYTICS,
    ],
    UserRole.USER: [
        Permission.CREATE_ALERTS,
        Permission.UPDATE_ALERTS,
        Permission.VIEW_ALERTS,
        Permission.CREATE_LOGS,
        Permission.VIEW_LOGS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ANALYTICS,
    ],
    UserRole.VIEWER: [
        Permission.VIEW_ALERTS,
        Permission.VIEW_LOGS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ANALYTICS,
    ],
}


def has_permission(user_role: UserRole, permission: str) -> bool:
    """Check if a role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(user_role, [])


def require_permission(permission: str):
    """Decorator to require a specific permission for an endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required permission: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(allowed_roles: List[UserRole]):
    """Decorator to require specific roles for an endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
