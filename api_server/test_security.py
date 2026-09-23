from fastapi.testclient import TestClient
from api_server.main import app

client = TestClient(app)

def test_auth_valid_student():
    response = client.post("/api/auth/login", json={"account_key": "student", "claimed_role": "student"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["id"] == "stu_014"
    assert data["user"]["role"] == "student"
    print("[PASS] Valid student authentication passed.")

def test_auth_invalid_mismatched_role():
    # Attempting to claim 'admin' with 'student' demo account
    response = client.post("/api/auth/login", json={"account_key": "student", "claimed_role": "admin"})
    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]
    print("[PASS] Wrong-role login rejection passed (HTTP 403 returned).")

def test_auth_invalid_trainer_claiming_student():
    response = client.post("/api/auth/login", json={"account_key": "trainer", "claimed_role": "student"})
    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]
    print("[PASS] Wrong-role trainer claiming student rejection passed (HTTP 403 returned).")

def test_student_forbidden_from_admin_endpoints():
    # Student attempting to access admin audit logs
    headers = {
        "x-user-id": "stu_014",
        "x-user-role": "student"
    }
    response = client.get("/api/admin/audit-logs", headers=headers)
    assert response.status_code == 403
    print("[PASS] Student blocked from admin audit logs (HTTP 403 returned).")

def test_trainer_access_allowed():
    headers = {
        "x-user-id": "trn_007",
        "x-user-role": "trainer"
    }
    response = client.get("/api/trainer/submissions", headers=headers)
    assert response.status_code == 200
    print("[PASS] Trainer authorized access to evaluation queue passed.")

if __name__ == "__main__":
    test_auth_valid_student()
    test_auth_invalid_mismatched_role()
    test_auth_invalid_trainer_claiming_student()
    test_student_forbidden_from_admin_endpoints()
    test_trainer_access_allowed()
    print("\nALL SERVER-ENFORCED SECURITY AND RBAC TESTS PASSED SUCCESSFULLY!")
