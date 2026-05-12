import pytest


# ---------------------------------------------------------------------------
# POST /api/query
# ---------------------------------------------------------------------------

def test_query_auto_creates_session_when_none_given(api_client, mock_rag_system):
    mock_rag_system.session_manager.create_session.return_value = "auto_sess"
    mock_rag_system.query.return_value = ("Python uses indentation.", [])

    resp = api_client.post("/api/query", json={"query": "What is Python?"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == "Python uses indentation."
    assert body["session_id"] == "auto_sess"
    assert isinstance(body["sources"], list)


def test_query_uses_provided_session_id(api_client, mock_rag_system):
    mock_rag_system.query.return_value = ("Answer.", [])

    resp = api_client.post("/api/query", json={"query": "Q", "session_id": "existing_sess"})

    assert resp.status_code == 200
    assert resp.json()["session_id"] == "existing_sess"
    mock_rag_system.session_manager.create_session.assert_not_called()


def test_query_propagates_sources(api_client, mock_rag_system):
    mock_rag_system.query.return_value = (
        "Python answer.",
        [{"label": "Python Basics - Lesson 1", "url": "https://example.com/lesson/1"}],
    )

    resp = api_client.post("/api/query", json={"query": "Explain Python"})

    sources = resp.json()["sources"]
    assert len(sources) == 1
    assert sources[0]["label"] == "Python Basics - Lesson 1"
    assert sources[0]["url"] == "https://example.com/lesson/1"


def test_query_source_url_may_be_null(api_client, mock_rag_system):
    mock_rag_system.query.return_value = ("Answer.", [{"label": "Course X - Lesson 2", "url": None}])

    resp = api_client.post("/api/query", json={"query": "Anything"})

    assert resp.json()["sources"][0]["url"] is None


def test_query_returns_500_on_rag_error(api_client, mock_rag_system):
    mock_rag_system.query.side_effect = RuntimeError("DB connection failed")

    resp = api_client.post("/api/query", json={"query": "Q"})

    assert resp.status_code == 500


def test_query_rejects_missing_query_field(api_client, mock_rag_system):
    resp = api_client.post("/api/query", json={"session_id": "s1"})

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/courses
# ---------------------------------------------------------------------------

def test_get_courses_returns_stats(api_client, mock_rag_system):
    mock_rag_system.get_course_analytics.return_value = {
        "total_courses": 3,
        "course_titles": ["Python", "JavaScript", "SQL"],
    }

    resp = api_client.get("/api/courses")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total_courses"] == 3
    assert body["course_titles"] == ["Python", "JavaScript", "SQL"]


def test_get_courses_returns_empty_when_no_courses(api_client, mock_rag_system):
    mock_rag_system.get_course_analytics.return_value = {"total_courses": 0, "course_titles": []}

    resp = api_client.get("/api/courses")

    assert resp.status_code == 200
    assert resp.json()["total_courses"] == 0
    assert resp.json()["course_titles"] == []


def test_get_courses_returns_500_on_error(api_client, mock_rag_system):
    mock_rag_system.get_course_analytics.side_effect = Exception("collection error")

    resp = api_client.get("/api/courses")

    assert resp.status_code == 500


# ---------------------------------------------------------------------------
# DELETE /api/session/{session_id}
# ---------------------------------------------------------------------------

def test_delete_session_clears_and_confirms(api_client, mock_rag_system):
    resp = api_client.delete("/api/session/sess_42")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "cleared"
    assert body["session_id"] == "sess_42"
    mock_rag_system.session_manager.clear_session.assert_called_once_with("sess_42")


def test_delete_session_returns_500_on_error(api_client, mock_rag_system):
    mock_rag_system.session_manager.clear_session.side_effect = Exception("session not found")

    resp = api_client.delete("/api/session/bad_sess")

    assert resp.status_code == 500
