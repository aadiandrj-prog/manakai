from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_demo_mode():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["demo_mode"] is True


def test_product_analyse_endpoint():
    response = client.post("/api/v1/products/analyse", json={"description": "portable rechargeable LED emergency lamp", "role": "manufacturer"})
    assert response.status_code == 200
    assert response.json()["mandatory_status"] == "UNVERIFIED"


def test_unknown_standard_is_404():
    assert client.get("/api/v1/standards/missing").status_code == 404


def test_unanswerable_query_discloses_boundary():
    response = client.post("/api/v1/qa", json={"query": "What is the exact unpublished rule?"})
    assert response.status_code == 200
    assert "could not verify" in response.json()["answer"]
