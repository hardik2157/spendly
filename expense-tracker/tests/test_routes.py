"""Backend route tests: status codes, rendering, placeholders and 404/405 handling."""

import pytest


# ------------------------------------------------------------------ #
# Public pages                                                        #
# ------------------------------------------------------------------ #

class TestLandingRoute:
    def test_returns_200(self, client):
        assert client.get("/").status_code == 200

    def test_renders_landing_template(self, client):
        html = client.get("/").get_data(as_text=True)
        assert "Know where your" in html
        assert "money goes" in html

    def test_title_is_set(self, client):
        html = client.get("/").get_data(as_text=True)
        assert "<title>Spendly — Track Every Rupee</title>" in html

    def test_only_get_is_allowed(self, client):
        assert client.post("/").status_code == 405


class TestLoginRoute:
    def test_get_returns_200(self, client):
        assert client.get("/login").status_code == 200

    def test_renders_login_template(self, client):
        html = client.get("/login").get_data(as_text=True)
        assert "Welcome back" in html
        assert "<title>Sign in — Spendly</title>" in html

    def test_form_posts_to_login(self, client):
        html = client.get("/login").get_data(as_text=True)
        assert 'method="POST"' in html
        assert 'action="/login"' in html

    def test_error_not_shown_by_default(self, client):
        html = client.get("/login").get_data(as_text=True)
        assert 'class="auth-error"' not in html

    @pytest.mark.xfail(reason="POST /login not implemented yet (Step 3)", strict=True)
    def test_post_valid_credentials_redirects(self, client):
        response = client.post("/login", data={
            "email": "nitish@example.com",
            "password": "password123",
        })
        assert response.status_code in (302, 303)

    def test_post_is_currently_405(self, client):
        # Documents the current state; remove once POST /login is implemented
        assert client.post("/login", data={}).status_code == 405


class TestRegisterRoute:
    def test_get_returns_200(self, client):
        assert client.get("/register").status_code == 200

    def test_renders_register_template(self, client):
        html = client.get("/register").get_data(as_text=True)
        assert "Create your account" in html
        assert "<title>Create account — Spendly</title>" in html

    def test_form_has_name_email_password_fields(self, client):
        html = client.get("/register").get_data(as_text=True)
        assert 'name="name"' in html
        assert 'name="email"' in html
        assert 'name="password"' in html

    def test_form_posts_to_register(self, client):
        html = client.get("/register").get_data(as_text=True)
        assert 'action="/register"' in html

    def test_post_is_currently_405(self, client):
        assert client.post("/register", data={}).status_code == 405

    @pytest.mark.xfail(reason="POST /register not implemented yet (Step 2)", strict=True)
    def test_post_valid_data_redirects(self, client):
        response = client.post("/register", data={
            "name": "Nitish Kumar",
            "email": "new.user@example.com",
            "password": "password123",
        })
        assert response.status_code in (302, 303)


# ------------------------------------------------------------------ #
# Placeholder routes                                                  #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("path, expected", [
    ("/logout", "Logout — coming in Step 3"),
    ("/profile", "Profile page — coming in Step 4"),
    ("/expenses/add", "Add expense — coming in Step 7"),
    ("/expenses/5/edit", "Edit expense — coming in Step 8"),
    ("/expenses/5/delete", "Delete expense — coming in Step 9"),
])
def test_placeholder_routes_return_expected_text(client, path, expected):
    response = client.get(path)
    assert response.status_code == 200
    assert response.get_data(as_text=True) == expected


@pytest.mark.parametrize("path", [
    "/expenses/abc/edit",
    "/expenses/abc/delete",
    "/expenses/1.5/edit",
    "/expenses/-1/edit",
])
def test_expense_routes_reject_non_integer_ids(client, path):
    assert client.get(path).status_code == 404


# ------------------------------------------------------------------ #
# Error handling                                                      #
# ------------------------------------------------------------------ #

def test_unknown_path_returns_404(client):
    assert client.get("/does-not-exist").status_code == 404


def test_landing_does_not_accept_post(client):
    assert client.post("/", data={}).status_code == 405


def test_static_css_is_served(client):
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["Content-Type"]


def test_static_js_is_served(client):
    response = client.get("/static/js/main.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["Content-Type"]


def test_missing_static_file_returns_404(client):
    assert client.get("/static/css/nope.css").status_code == 404
