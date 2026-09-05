from fastapi.testclient import TestClient


def application_payload() -> dict[str, str]:
    return {
        "company": "Example Company",
        "position": "Python Developer",
        "url": "https://example.com/job",
        "description": "Backend development",
        "status": "new",
        "source": "test",
    }


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "job-app-platform",
    }


def test_list_applications_is_empty(client: TestClient) -> None:
    response = client.get("/applications")

    assert response.status_code == 200
    assert response.json() == {"applications": []}


def test_create_application(client: TestClient) -> None:
    response = client.post("/applications", json=application_payload())

    assert response.status_code == 200
    body = response.json()
    application = body["application"]

    assert body["message"] == "Application created"
    assert application["id"] == 1
    assert application["company"] == "Example Company"
    assert application["position"] == "Python Developer"
    assert application["status"] == "new"
    assert application["source"] == "test"
    assert application["created_at"]
    assert application["updated_at"]


def test_get_application(client: TestClient) -> None:
    create_response = client.post("/applications", json=application_payload())
    application_id = create_response.json()["application"]["id"]

    response = client.get(f"/applications/{application_id}")

    assert response.status_code == 200
    assert response.json()["id"] == application_id
    assert response.json()["company"] == "Example Company"


def test_get_missing_application_returns_not_found(client: TestClient) -> None:
    response = client.get("/applications/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application not found"}


def test_update_application(client: TestClient) -> None:
    create_response = client.post("/applications", json=application_payload())
    application_id = create_response.json()["application"]["id"]

    response = client.patch(
        f"/applications/{application_id}",
        json={"status": "interview", "company": "Updated Company"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "interview"
    assert response.json()["company"] == "Updated Company"
    assert response.json()["position"] == "Python Developer"


def test_create_application_rejects_empty_company(client: TestClient) -> None:
    payload = application_payload()
    payload["company"] = ""

    response = client.post("/applications", json=payload)

    assert response.status_code == 422
