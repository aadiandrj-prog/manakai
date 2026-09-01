from app.main import app


def test_openapi_contains_required_integration_endpoints():
    paths = app.openapi()["paths"]
    assert {
        "/api/v1/standards",
        "/api/v1/standards/{standard_id}",
        "/api/v1/standards/{standard_id}/relationships",
        "/api/v1/products/analyse",
        "/api/v1/compliance/{profile_id}",
        "/api/v1/compliance/{profile_id}/journey",
        "/api/v1/labs",
        "/api/v1/labs/search",
        "/api/v1/qa",
        "/api/v1/documents/{document_id}",
    }.issubset(paths)
