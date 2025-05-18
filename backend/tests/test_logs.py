"""Tests for security logs endpoints."""
import pytest
from fastapi import status


def test_create_log(client, test_user_data, test_log_data):
    """Test creating a security log."""
    # Register and login
    client.post("/api/auth/register", json=test_user_data)
    login_response = client.post("/api/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create log
    response = client.post("/api/logs/", json=test_log_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["event_type"] == test_log_data["event_type"]
    assert data["severity"] == test_log_data["severity"]
    assert "id" in data


def test_get_logs(client, test_user_data, test_log_data):
    """Test retrieving security logs."""
    # Register and login
    client.post("/api/auth/register", json=test_user_data)
    login_response = client.post("/api/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a log
    client.post("/api/logs/", json=test_log_data, headers=headers)
    
    # Get logs
    response = client.get("/api/logs/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["event_type"] == test_log_data["event_type"]


def test_get_log_by_id(client, test_user_data, test_log_data):
    """Test retrieving a specific log by ID."""
    # Register and login
    client.post("/api/auth/register", json=test_user_data)
    login_response = client.post("/api/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a log
    create_response = client.post("/api/logs/", json=test_log_data, headers=headers)
    log_id = create_response.json()["id"]
    
    # Get log by ID
    response = client.get(f"/api/logs/{log_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == log_id
    assert data["event_type"] == test_log_data["event_type"]


def test_filter_logs_by_severity(client, test_user_data, test_log_data):
    """Test filtering logs by severity."""
    # Register and login
    client.post("/api/auth/register", json=test_user_data)
    login_response = client.post("/api/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create logs with different severities
    client.post("/api/logs/", json={**test_log_data, "severity": "low"}, headers=headers)
    client.post("/api/logs/", json={**test_log_data, "severity": "high"}, headers=headers)
    
    # Filter by high severity
    response = client.get("/api/logs/?severity=high", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(log["severity"] == "high" for log in data)


def test_unauthorized_access(client, test_log_data):
    """Test accessing logs without authentication."""
    response = client.get("/api/logs/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
