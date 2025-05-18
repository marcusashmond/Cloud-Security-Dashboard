"""Tests for RBAC permissions."""
import pytest

from app.db.models import UserRole
from app.core.permissions import has_permission, Permission, ROLE_PERMISSIONS


def test_admin_has_all_permissions():
    """Test that admin role has all permissions."""
    assert has_permission(UserRole.ADMIN, Permission.MANAGE_USERS) is True
    assert has_permission(UserRole.ADMIN, Permission.DELETE_LOGS) is True
    assert has_permission(UserRole.ADMIN, Permission.VIEW_AUDIT_LOGS) is True
    assert has_permission(UserRole.ADMIN, Permission.EXPORT_DATA) is True


def test_user_has_limited_permissions():
    """Test that user role has limited permissions."""
    assert has_permission(UserRole.USER, Permission.VIEW_LOGS) is True
    assert has_permission(UserRole.USER, Permission.CREATE_ALERTS) is True
    assert has_permission(UserRole.USER, Permission.VIEW_DASHBOARD) is True
    
    # Should not have admin permissions
    assert has_permission(UserRole.USER, Permission.MANAGE_USERS) is False
    assert has_permission(UserRole.USER, Permission.DELETE_LOGS) is False


def test_viewer_read_only_permissions():
    """Test that viewer role only has read permissions."""
    assert has_permission(UserRole.VIEWER, Permission.VIEW_LOGS) is True
    assert has_permission(UserRole.VIEWER, Permission.VIEW_DASHBOARD) is True
    assert has_permission(UserRole.VIEWER, Permission.VIEW_ANALYTICS) is True
    
    # Should not have write permissions
    assert has_permission(UserRole.VIEWER, Permission.CREATE_ALERTS) is False
    assert has_permission(UserRole.VIEWER, Permission.UPDATE_ALERTS) is False
    assert has_permission(UserRole.VIEWER, Permission.DELETE_LOGS) is False


def test_all_roles_defined():
    """Test that all user roles have permission mappings."""
    for role in UserRole:
        assert role in ROLE_PERMISSIONS
        assert len(ROLE_PERMISSIONS[role]) > 0
