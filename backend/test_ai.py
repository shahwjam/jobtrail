RESUME = "Python developer with FastAPI, PostgreSQL and React experience. " * 3


def make_application(client, **overrides):
    payload = {
        "company": "Acme Corp",
        "position": "Backend Engineer",
        "job_description": "We need a Python engineer who knows FastAPI and PostgreSQL.",
        **overrides,
    }
    return client.post("/applications", json=payload).json()


# === TASK-016: cover letters ===

def test_cover_letter_generated(client, fake_ai):
    application = make_application(client)

    response = client.post(f"/applications/{application['id']}/cover-letter", json={"resume_text": RESUME})

    assert response.status_code == 200
    assert response.json() == {"application_id": application["id"], "cover_letter": fake_ai.reply}
    # The prompt Claude saw includes the job and the resume
    prompt = fake_ai.calls[0]["prompt"]
    assert "Acme Corp" in prompt and "FastAPI" in prompt and RESUME.strip() in prompt


def test_cover_letter_application_not_found(client, fake_ai):
    response = client.post("/applications/999/cover-letter", json={"resume_text": RESUME})
    assert response.status_code == 404
    assert fake_ai.calls == []


def test_cover_letter_requires_job_description(client, fake_ai):
    application = make_application(client, job_description=None)
    response = client.post(f"/applications/{application['id']}/cover-letter", json={"resume_text": RESUME})
    assert response.status_code == 400
    assert fake_ai.calls == []   # rejected before spending an API call


def test_cover_letter_resume_too_short(client):
    application = make_application(client)
    response = client.post(f"/applications/{application['id']}/cover-letter", json={"resume_text": "hi"})
    assert response.status_code == 422


# === TASK-017: prompt templates ===

def test_cover_letter_uses_template_and_tone(client, fake_ai):
    application = make_application(client)

    client.post(
        f"/applications/{application['id']}/cover-letter",
        json={"resume_text": RESUME, "tone": "concise"},
    )

    call = fake_ai.calls[0]
    assert "untrusted data" in call["system"]
    assert "<resume>" in call["prompt"]
    assert "three short paragraphs" in call["prompt"]


def test_cover_letter_rejects_unknown_tone(client):
    application = make_application(client)
    response = client.post(
        f"/applications/{application['id']}/cover-letter",
        json={"resume_text": RESUME, "tone": "pirate"},
    )
    assert response.status_code == 422
