def test_health_reports_demo_mode(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["demo_mode"] is True


def test_product_analyse_endpoint(client):
    response = client.post("/api/v1/products/analyse", json={"description": "portable rechargeable LED emergency lamp", "role": "manufacturer"})
    assert response.status_code == 200
    assert response.json()["mandatory_status"] == "UNVERIFIED"


def test_unknown_standard_is_404(client):
    assert client.get("/api/v1/standards/missing").status_code == 404


def test_unanswerable_query_discloses_boundary(client):
    response = client.post("/api/v1/qa", json={"query": "What is the exact unpublished rule?"})
    assert response.status_code == 200
    assert "could not verify" in response.json()["answer"]


def test_seeded_endpoints_and_relationships(client):
    standards = client.get("/api/v1/standards")
    labs = client.get("/api/v1/labs")
    relationships = client.get("/api/v1/standards/is-10322-5-8/relationships")
    document = client.get("/api/v1/documents/doc-emergency-scope")
    assert standards.status_code == labs.status_code == relationships.status_code == document.status_code == 200
    assert len(standards.json()) == 5
    assert len(labs.json()) == 4
    assert relationships.json()[0]["target_standard"]["id"] == "is-302-2-15"
    assert document.json()["source_kind"] == "DEMO"


def test_lab_search_combines_standard_and_location(client):
    response = client.post(
        "/api/v1/labs/search",
        json={"query": "", "standard_number": "IS 10322 (Part 5/Sec 8)", "location": "Delhi"},
    )
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["lab-delhi"]
