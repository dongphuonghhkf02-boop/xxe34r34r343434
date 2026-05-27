"""
Smoke test for policies API.

Coverage:
  1) Public  GET /api/policies              → 3 items (cookie/privacy/terms) with defaults
  2) Public  GET /api/policies/cookie       → single item
  3) Public  GET /api/policies/unknown      → 404
  4) Admin   PUT /api/admin/policies/cookie without token → 401
  5) Admin   PUT /api/admin/policies/cookie with regular user → 403
  6) Admin   POST /api/auth/login admin → token
  7) Admin   PUT /api/admin/policies/terms (button_label, title, html_content) → 200
  8) Verify  GET /api/policies/terms returns the updated content
  9) Admin   PUT /api/admin/policies/cookie with empty html → preserves explicit empty? (skip; only required path)
 10) Reset terms to original (idempotent re-update)
"""
import os
import sys
import time
import requests

BASE = os.environ.get("API_BASE", "http://localhost:8001/api")

ADMIN_EMAIL = "admin@tamis.ua"
ADMIN_PASSWORD = "admin1234"
USER_EMAIL = "test@tamis.ua"
USER_PASSWORD = "test1234"


def color(ok: bool) -> str:
    return "\033[92m✓\033[0m" if ok else "\033[91m✗\033[0m"


def step(name, cond, detail=""):
    print(f"  {color(cond)} {name}{'  — ' + detail if detail else ''}")
    if not cond:
        global FAILED
        FAILED += 1


FAILED = 0


def login(email, password):
    r = requests.post(f"{BASE}/auth/login", json={"email": email, "password": password}, timeout=10)
    r.raise_for_status()
    return r.json().get("token") or r.json().get("access_token") or r.json().get("data", {}).get("token")


def main():
    global FAILED
    print("=== Policies API smoke test ===")
    print(f"BASE: {BASE}\n")

    # 1. Public list
    r = requests.get(f"{BASE}/policies", timeout=10)
    step("GET /policies → 200", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        items = r.json().get("items", [])
        types = sorted([it["type"] for it in items])
        step("Has 3 items (cookie, privacy, terms)", types == ["cookie", "privacy", "terms"], f"got={types}")
        for it in items:
            step(
                f"  type={it['type']} has button_label + title + html",
                bool(it.get("button_label")) and bool(it.get("title")) and bool(it.get("html_content")),
                f"button={it.get('button_label')!r}, title={it.get('title')!r}, html_len={len(it.get('html_content',''))}",
            )

    # 2. Single policy
    r = requests.get(f"{BASE}/policies/cookie", timeout=10)
    step("GET /policies/cookie → 200", r.status_code == 200)
    if r.status_code == 200:
        body = r.json()
        step("  cookie has button_label='Cookie Policy'", body.get("button_label") == "Cookie Policy",
             f"got={body.get('button_label')!r}")

    # 3. Unknown type
    r = requests.get(f"{BASE}/policies/nonexistent", timeout=10)
    step("GET /policies/nonexistent → 404", r.status_code == 404, f"status={r.status_code}")

    # 4. Admin endpoint w/o token
    r = requests.put(f"{BASE}/admin/policies/cookie", json={"title": "x"}, timeout=10)
    step("PUT /admin/policies/cookie w/o token → 401", r.status_code == 401, f"status={r.status_code}")

    # 5. Regular user → 403
    try:
        user_token = login(USER_EMAIL, USER_PASSWORD)
    except Exception as e:
        print(f"  ! Could not log in as regular user: {e}")
        user_token = None

    if user_token:
        r = requests.put(
            f"{BASE}/admin/policies/cookie",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "hacked"},
            timeout=10,
        )
        step("PUT /admin/policies/cookie as test user → 403", r.status_code == 403, f"status={r.status_code}")

    # 6. Admin login
    try:
        admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    except Exception as e:
        print(f"  ✗ Admin login failed: {e}")
        FAILED += 1
        sys.exit(1)
    step("Admin login → token", bool(admin_token), f"token_len={len(admin_token or '')}")

    # 7. Update terms
    new_terms = {
        "button_label": "Terms of Use (TEST)",
        "title": "Тестова політика умов",
        "html_content": "<h2>Тест</h2><p>Це тест.</p>",
    }
    r = requests.put(
        f"{BASE}/admin/policies/terms",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=new_terms,
        timeout=10,
    )
    step("PUT /admin/policies/terms → 200", r.status_code == 200, f"status={r.status_code}, body={r.text[:200]}")
    if r.status_code == 200:
        body = r.json()
        step("  returned button_label updated", body.get("button_label") == new_terms["button_label"])
        step("  returned title updated", body.get("title") == new_terms["title"])
        step("  returned html updated", body.get("html_content") == new_terms["html_content"])

    # 8. Public reflects change
    time.sleep(0.2)
    r = requests.get(f"{BASE}/policies/terms", timeout=10)
    if r.status_code == 200:
        body = r.json()
        step("Public /policies/terms reflects new button_label", body.get("button_label") == new_terms["button_label"])
        step("Public /policies/terms reflects new title", body.get("title") == new_terms["title"])
        step("Public /policies/terms reflects new html", body.get("html_content") == new_terms["html_content"])

    # 9. Restore default terms (full content)
    full_terms_html = (
        "<h2>Прийняття умов</h2>"
        "<p>Використовуючи сайт <strong>TAMIS АГРО</strong>, ви погоджуєтесь "
        "із цими Умовами користування. Якщо ви не згодні — будь ласка, "
        "припиніть використання сайту.</p>"
        "<h2>Опис сервісу</h2>"
        "<p>Сайт надає можливість ознайомитися з каталогом агро-продукції, "
        "оформити замовлення, отримати консультацію та інформацію щодо "
        "сільськогосподарських культур.</p>"
        "<h2>Реєстрація та обліковий запис</h2>"
        "<ul>"
        "<li>Користувач зобов'язаний надавати правдиві дані під час реєстрації.</li>"
        "<li>Збереження пароля — відповідальність користувача.</li>"
        "<li>Адміністрація має право заблокувати акаунт у разі порушення Умов.</li>"
        "</ul>"
        "<h2>Замовлення та оплата</h2>"
        "<ol>"
        "<li>Ціни вказані в гривнях з ПДВ.</li>"
        "<li>Замовлення вважається підтвердженим після зв'язку менеджера.</li>"
        "<li>Доставка здійснюється згідно з тарифами обраного перевізника.</li>"
        "</ol>"
        "<h2>Інтелектуальна власність</h2>"
        "<p>Усі матеріали сайту (тексти, фото, логотипи) є власністю "
        "TAMIS АГРО або використовуються за ліцензією. Копіювання без "
        "дозволу заборонено.</p>"
        "<h2>Обмеження відповідальності</h2>"
        "<p>Сайт надається «як є». Ми не несемо відповідальності за "
        "тимчасову недоступність, помилки в описах товарів чи дії третіх сторін.</p>"
        "<h2>Контакти</h2>"
        "<p>З питань щодо Умов: <a href=\"mailto:tamisagro@gmail.com\">tamisagro@gmail.com</a></p>"
    )
    original = {
        "button_label": "Terms of Use",
        "title": "Умови користування сайтом",
        "html_content": full_terms_html,
    }
    r = requests.put(
        f"{BASE}/admin/policies/terms",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=original,
        timeout=10,
    )
    step("Restore terms via PUT → 200", r.status_code == 200, f"status={r.status_code}")

    # 10. Admin list
    r = requests.get(
        f"{BASE}/admin/policies",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10,
    )
    step("GET /admin/policies (admin) → 200", r.status_code == 200, f"status={r.status_code}")

    # Summary
    print()
    if FAILED:
        print(f"\033[91m{FAILED} step(s) failed.\033[0m")
        sys.exit(1)
    else:
        print("\033[92mAll policy API checks passed.\033[0m")


if __name__ == "__main__":
    main()
