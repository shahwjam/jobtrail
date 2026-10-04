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


# === TASK-018: resume match score ===

MATCH_REPLY = (
    '{"score": 80, "matched_keywords": ["Python", "FastAPI"], '
    '"missing_keywords": ["Kubernetes"], "summary": "Strong backend fit."}'
)


def test_match_score_saved_and_shown_on_application(client, fake_ai):
    fake_ai.reply = MATCH_REPLY
    application = make_application(client)

    response = client.post(f"/applications/{application['id']}/match-score", json={"resume_text": RESUME})

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 80
    assert data["matched_keywords"] == ["Python", "FastAPI"]
    assert data["missing_keywords"] == ["Kubernetes"]
    # The score now appears on the application itself, for the dashboard card
    assert client.get("/applications").json()[0]["match_score"] == 80
    assert client.get(f"/applications/{application['id']}/match-score").json()["score"] == 80


def test_match_score_rerun_overwrites(client, fake_ai):
    application = make_application(client)
    fake_ai.reply = MATCH_REPLY
    client.post(f"/applications/{application['id']}/match-score", json={"resume_text": RESUME})

    fake_ai.reply = MATCH_REPLY.replace("80", "55")
    client.post(f"/applications/{application['id']}/match-score", json={"resume_text": RESUME + " v2"})

    assert client.get("/applications").json()[0]["match_score"] == 55


def test_match_score_tolerates_code_fence(client, fake_ai):
    fake_ai.reply = f"Here you go:\n```json\n{MATCH_REPLY}\n```"
    application = make_application(client)
    response = client.post(f"/applications/{application['id']}/match-score", json={"resume_text": RESUME})
    assert response.status_code == 200
    assert response.json()["score"] == 80


def test_match_score_garbage_reply_is_502(client, fake_ai):
    fake_ai.reply = "I can't score this."
    application = make_application(client)
    response = client.post(f"/applications/{application['id']}/match-score", json={"resume_text": RESUME})
    assert response.status_code == 502


def test_match_score_out_of_range_is_502(client, fake_ai):
    fake_ai.reply = MATCH_REPLY.replace("80", "140")
    application = make_application(client)
    response = client.post(f"/applications/{application['id']}/match-score", json={"resume_text": RESUME})
    assert response.status_code == 502


def test_get_match_score_before_any_run_is_404(client):
    application = make_application(client)
    assert client.get(f"/applications/{application['id']}/match-score").status_code == 404


def test_new_application_has_no_score(client):
    assert make_application(client)["match_score"] is None
