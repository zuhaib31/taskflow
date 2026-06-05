"""
Integration tests for application routes.

These tests use Flask's test client to make requests without running
a real server. They focus on routing, authentication gating, and
configuration behavior - the parts that don't depend on database data.

Routes that require real database queries are intentionally not tested
here, as mocking full query results adds complexity without much value
for this project's scope.
"""


class TestHealthEndpoint:
    """Tests for the /health endpoint used by Docker and monitoring."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json_status(self, client):
        response = client.get("/health")
        assert response.is_json
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "taskflow"


class TestLandingPage:
    """Tests for the public landing page."""

    def test_landing_page_loads_when_logged_out(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_landing_page_contains_app_name(self, client):
        response = client.get("/")
        assert b"TaskFlow" in response.data


class TestAuthenticationGating:
    """
    Tests that protected routes redirect to login when the user is
    not authenticated. These redirects happen in the @login_required
    decorator, before any database access.
    """

    def test_dashboard_redirects_when_not_logged_in(self, client):
        response = client.get("/dashboard")
        assert response.status_code == 302
        assert "/login" in response.location

    def test_projects_list_redirects_when_not_logged_in(self, client):
        response = client.get("/projects/")
        assert response.status_code == 302
        assert "/login" in response.location

    def test_new_project_redirects_when_not_logged_in(self, client):
        response = client.get("/projects/new")
        assert response.status_code == 302
        assert "/login" in response.location


class TestLoginPage:
    """Tests for the login page rendering."""

    def test_login_page_loads(self, client):
        response = client.get("/login")
        assert response.status_code == 200

    def test_login_page_has_form(self, client):
        response = client.get("/login")
        assert b"email" in response.data.lower()
        assert b"password" in response.data.lower()


class TestRegisterPage:
    """Tests for the registration page rendering."""

    def test_register_page_loads(self, client):
        response = client.get("/register")
        assert response.status_code == 200

    def test_register_page_has_form(self, client):
        response = client.get("/register")
        assert b"username" in response.data.lower()
        assert b"email" in response.data.lower()


class TestNotFoundHandling:
    """Tests for the custom 404 error page."""

    def test_unknown_route_returns_404(self, client):
        response = client.get("/this-page-does-not-exist")
        assert response.status_code == 404

    def test_404_page_is_friendly(self, client):
        response = client.get("/this-page-does-not-exist")
        assert b"not found" in response.data.lower() or b"404" in response.data
