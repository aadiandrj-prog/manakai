def test_conversation_api_lifecycle_works_without_ai(client):
    created = client.post("/api/v1/conversations", json={"language": "auto"})
    assert created.status_code == 200
    conversation_id = created.json()["conversation_id"]
    response = client.post(f"/api/v1/conversations/{conversation_id}/messages", json={"message": "What is BIS?", "language": "auto"})
    assert response.status_code == 200
    assert response.json()["used_fallback"] is True
    fetched = client.get(f"/api/v1/conversations/{conversation_id}")
    assert fetched.status_code == 200
    assert len(fetched.json()["messages"]) == 2
