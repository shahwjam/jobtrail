def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_application(client):
    payload = {"company": "Acme Corp", "position": "Backend Engineer", "status": "Applied"}
    response = client.post("/applications", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Acme Corp"
    assert data["position"] == "Backend Engineer"
    assert data["status"] == "Applied"
    assert "id" in data            # the DB assigned an id
    assert "created_at" in data    # the DB stamped a timestamp


def test_get_applications_empty(client):
    response = client.get("/applications")
    assert response.status_code == 200
    assert response.json() == []   # clean DB → empty list


def test_create_then_get(client):
    client.post("/applications", json={"company": "Globex", "position": "SWE"})
    response = client.get("/applications")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Globex"


def test_invalid_status_rejected(client):
    payload = {"company": "Initech", "position": "SWE", "status": "no"}
    response = client.post("/applications", json=payload)
    assert response.status_code == 422   # the TASK-008 validation, now tested


def test_empty_company_rejected(client):
    payload = {"company": "", "position": "SWE"}
    response = client.post("/applications", json=payload)
    assert response.status_code == 422   # min_length=1 constraint
