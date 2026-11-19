"""Front-end tests: rendered pages, navigation, form validation, responsive layout and theme.

Run with:  pytest tests/frontend
Requires:  pip install playwright  &&  python -m playwright install chromium
"""

import pytest

pytest.importorskip("playwright.sync_api")

from playwright.sync_api import expect  # noqa: E402

PINK_PAGE_BG = "rgb(255, 245, 249)"   # --paper   #fff5f9
PINK_ACCENT = "rgb(214, 51, 108)"     # --accent  #d6336c
PINK_INK = "rgb(61, 18, 41)"          # --ink     #3d1229


def _goto(page, base, path):
    page.goto(base + path)
    page.wait_for_load_state("domcontentloaded")
    return page


# ------------------------------------------------------------------ #
# Landing page                                                        #
# ------------------------------------------------------------------ #

class TestLandingPage:
    def test_title(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        expect(page).to_have_title("Spendly — Track Every Rupee")

    def test_hero_heading_visible(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        expect(page.locator(".hero-title")).to_contain_text("Know where your")
        expect(page.locator(".hero-title em")).to_have_text("money goes")

    def test_hero_buttons_visible(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        expect(page.locator(".hero-actions .btn-primary")).to_have_text("Start tracking free")
        expect(page.locator(".hero-actions .btn-ghost")).to_have_text("Sign in")

    def test_three_feature_cards(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        cards = page.locator(".feature-card")
        expect(cards).to_have_count(3)
        expect(cards.nth(0).locator(".feature-title")).to_have_text("Log expenses instantly")
        expect(cards.nth(1).locator(".feature-title")).to_have_text("Understand your patterns")
        expect(cards.nth(2).locator(".feature-title")).to_have_text("Filter by time period")

    def test_mock_chart_has_four_categories(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        expect(page.locator(".mock-bar-row")).to_have_count(4)
        expect(page.locator(".mock-total")).to_have_text("₹12,450")

    def test_mock_bar_widths(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        widths = page.locator(".mock-bar").evaluate_all(
            "els => els.map(e => e.style.width)"
        )
        assert widths == ["72%", "52%", "33%", "28%"]

    def test_hero_start_button_navigates_to_register(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        page.click(".hero-actions .btn-primary")
        expect(page).to_have_url(live_server_url + "/register")

    def test_hero_sign_in_navigates_to_login(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        page.click(".hero-actions .btn-ghost")
        expect(page).to_have_url(live_server_url + "/login")

    def test_bottom_cta_navigates_to_register(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        page.click(".cta-section .btn-primary")
        expect(page).to_have_url(live_server_url + "/register")


# ------------------------------------------------------------------ #
# Global navigation and footer                                        #
# ------------------------------------------------------------------ #

class TestGlobalChrome:
    @pytest.mark.parametrize("path", ["/", "/login", "/register"])
    def test_navbar_and_footer_present(self, page, live_server_url, path):
        _goto(page, live_server_url, path)
        expect(page.locator("nav.navbar .brand-name")).to_have_text("Spendly")
        expect(page.locator("footer.footer .footer-copy")).to_have_text(
            "Track every rupee. Own your finances."
        )

    def test_brand_link_returns_home(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        page.click("a.nav-brand")
        expect(page).to_have_url(live_server_url + "/")

    def test_navbar_sign_in_link(self, page, live_server_url):
        _goto(page, live_server_url, "/register")
        page.click(".nav-links a:not(.nav-cta)")
        expect(page).to_have_url(live_server_url + "/login")

    def test_navbar_get_started_link(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        page.click(".nav-cta")
        expect(page).to_have_url(live_server_url + "/register")

    def test_navbar_is_sticky(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        assert page.eval_on_selector(".navbar", "e => getComputedStyle(e).position") == "sticky"


# ------------------------------------------------------------------ #
# Login page                                                          #
# ------------------------------------------------------------------ #

class TestLoginPage:
    def test_title_and_heading(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        expect(page).to_have_title("Sign in — Spendly")
        expect(page.locator(".auth-title")).to_have_text("Welcome back")

    def test_email_field_is_focused_on_load(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        expect(page.locator("#email")).to_be_focused()

    def test_empty_submit_is_blocked_by_browser(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        page.click("button.btn-submit")
        assert page.eval_on_selector("#email", "e => e.validity.valueMissing") is True
        expect(page).to_have_url(live_server_url + "/login")

    def test_invalid_email_is_blocked(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        page.fill("#email", "notanemail")
        page.fill("#password", "secret")
        page.click("button.btn-submit")
        assert page.eval_on_selector("#email", "e => e.validity.typeMismatch") is True
        expect(page).to_have_url(live_server_url + "/login")

    def test_empty_password_is_blocked(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        page.fill("#email", "nitish@example.com")
        page.click("button.btn-submit")
        assert page.eval_on_selector("#password", "e => e.validity.valueMissing") is True

    def test_password_input_masks_text(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        expect(page.locator("#password")).to_have_attribute("type", "password")

    def test_create_account_link(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        page.click(".auth-switch a")
        expect(page).to_have_url(live_server_url + "/register")


# ------------------------------------------------------------------ #
# Register page                                                       #
# ------------------------------------------------------------------ #

class TestRegisterPage:
    def test_title_and_heading(self, page, live_server_url):
        _goto(page, live_server_url, "/register")
        expect(page).to_have_title("Create account — Spendly")
        expect(page.locator(".auth-title")).to_have_text("Create your account")

    def test_name_field_is_focused_on_load(self, page, live_server_url):
        _goto(page, live_server_url, "/register")
        expect(page.locator("#name")).to_be_focused()

    def test_all_fields_are_required(self, page, live_server_url):
        _goto(page, live_server_url, "/register")
        for field in ("#name", "#email", "#password"):
            assert page.eval_on_selector(field, "e => e.required") is True

    def test_password_placeholder_mentions_minimum(self, page, live_server_url):
        _goto(page, live_server_url, "/register")
        expect(page.locator("#password")).to_have_attribute("placeholder", "Min. 8 characters")

    def test_empty_name_is_blocked(self, page, live_server_url):
        _goto(page, live_server_url, "/register")
        page.fill("#email", "nitish@example.com")
        page.fill("#password", "password123")
        page.click("button.btn-submit")
        assert page.eval_on_selector("#name", "e => e.validity.valueMissing") is True

    def test_invalid_email_is_blocked(self, page, live_server_url):
        _goto(page, live_server_url, "/register")
        page.fill("#name", "Nitish")
        page.fill("#email", "bad-email")
        page.fill("#password", "password123")
        page.click("button.btn-submit")
        assert page.eval_on_selector("#email", "e => e.validity.typeMismatch") is True

    def test_sign_in_link(self, page, live_server_url):
        _goto(page, live_server_url, "/register")
        page.click(".auth-switch a")
        expect(page).to_have_url(live_server_url + "/login")


# ------------------------------------------------------------------ #
# Theme (pink)                                                        #
# ------------------------------------------------------------------ #

class TestPinkTheme:
    def test_page_background_is_pink(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        assert page.eval_on_selector("body", "e => getComputedStyle(e).backgroundColor") == PINK_PAGE_BG

    def test_text_color_is_plum(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        assert page.eval_on_selector("body", "e => getComputedStyle(e).color") == PINK_INK

    def test_hero_accent_is_pink(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        assert page.eval_on_selector(".hero-title em", "e => getComputedStyle(e).color") == PINK_ACCENT

    def test_primary_button_hover_turns_pink(self, page, live_server_url):
        _goto(page, live_server_url, "/")
        button = page.locator(".hero-actions .btn-primary")
        button.hover()
        page.wait_for_timeout(300)  # transition is 0.2s
        assert button.evaluate("e => getComputedStyle(e).backgroundColor") == PINK_ACCENT

    def test_theme_applies_on_auth_pages(self, page, live_server_url):
        _goto(page, live_server_url, "/login")
        assert page.eval_on_selector("body", "e => getComputedStyle(e).backgroundColor") == PINK_PAGE_BG


# ------------------------------------------------------------------ #
# Responsive layout                                                   #
# ------------------------------------------------------------------ #

class TestResponsive:
    def test_desktop_shows_mock_card(self, page, live_server_url):
        page.set_viewport_size({"width": 1280, "height": 800})
        _goto(page, live_server_url, "/")
        expect(page.locator(".mock-card")).to_be_visible()

    def test_tablet_hides_mock_card(self, page, live_server_url):
        page.set_viewport_size({"width": 800, "height": 900})
        _goto(page, live_server_url, "/")
        expect(page.locator(".mock-card")).to_be_hidden()

    def test_tablet_stacks_features(self, page, live_server_url):
        page.set_viewport_size({"width": 800, "height": 900})
        _goto(page, live_server_url, "/")
        columns = page.eval_on_selector(".features-inner", "e => getComputedStyle(e).gridTemplateColumns")
        assert len(columns.split()) == 1

    def test_mobile_hides_text_nav_link(self, page, live_server_url):
        page.set_viewport_size({"width": 400, "height": 800})
        _goto(page, live_server_url, "/")
        expect(page.locator(".nav-links a:not(.nav-cta)")).to_be_hidden()
        expect(page.locator(".nav-cta")).to_be_visible()

    def test_mobile_keeps_cta_visible(self, page, live_server_url):
        page.set_viewport_size({"width": 400, "height": 800})
        _goto(page, live_server_url, "/")
        expect(page.locator(".hero-actions .btn-primary")).to_be_visible()

    def test_desktop_nav_text_link_visible(self, page, live_server_url):
        page.set_viewport_size({"width": 1280, "height": 800})
        _goto(page, live_server_url, "/")
        expect(page.locator(".nav-links a:not(.nav-cta)")).to_be_visible()


# ------------------------------------------------------------------ #
# Browser health                                                      #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("path", ["/", "/login", "/register"])
def test_no_javascript_errors(page, live_server_url, path):
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    _goto(page, live_server_url, path)
    assert errors == []


@pytest.mark.parametrize("path", ["/", "/login", "/register"])
def test_stylesheet_loaded(page, live_server_url, path):
    _goto(page, live_server_url, path)
    loaded = page.evaluate(
        "() => [...document.styleSheets].some(s => s.href && s.href.endsWith('/static/css/style.css'))"
    )
    assert loaded
