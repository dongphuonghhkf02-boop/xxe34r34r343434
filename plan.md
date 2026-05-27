# TAMIS АГРО — План: модульна CRM/Продажі в адмінці (Orders/Payments/Users/Abandoned Carts/Upsells)

## 1) Objectives
- Додати **модульний** backend-блок CRM/Продажів для адмінки: контроль замовлень, оплат (COD/переказ), користувачів, покинутих кошиків і допродажів.
- Забезпечити **backward-compatible** розширення існуючих public flow (cart → checkout → order), без поломок.
- Дати адмінам можливість: фільтрувати/оновлювати статуси, підтверджувати оплату, бачити контактні дані, керувати upsell-правилами.

## 2) Implementation Steps

### Phase 1 — Core POC (isolated, must pass before масштабування)
**Core workflow:** bank-transfer підтвердження оплати + відображення в адмінці (найризиковіше через стани/аудит/доказ оплати).
1. Створити модуль `/app/backend/sales/` (порожній каркас як `products/`).
2. Додати мінімальний POC API (admin-only):
   - `GET /api/admin/sales/orders?payment_status=`
   - `POST /api/admin/sales/orders/{id}/payment/confirm`
   - `POST /api/admin/sales/orders/{id}/payment/upload-proof` (multipart)
3. Додати migration/backfill для існуючих `orders` (payment_status/method/internal_status) + індекси.
4. Написати маленький **python script** (в `backend/scripts/`) який:
   - створює demo order (bank_transfer)
   - завантажує proof
   - підтверджує оплату
   - перевіряє, що order має paid_at/paid_amount/status
5. Fix until works (не рухатись далі, поки POC не зелений).

**POC user stories (5):**
1. Як адмін, я бачу список замовлень зі статусом `awaiting_confirmation`.
2. Як адмін, я відкриваю замовлення і бачу контактні дані отримувача.
3. Як адмін, я завантажую proof оплати і бачу URL.
4. Як адмін, я натискаю “Підтвердити оплату” і статус стає `paid`.
5. Як адмін, я бачу timestamp `paid_at` після підтвердження.

### Phase 2 — V1 App Development (backend module + minimal admin UI)
**Backend (модульність — НЕ моноліт):**
1. Реалізувати структуру `sales/`:
   - `models.py` (OrderExt, PaymentEvent, AbandonedCart, UpsellRule, UserSummary)
   - `security.py` (reuse admin dep)
   - `utils.py` (filters/pagination/iso)
   - `seed.py` (migrations/backfill)
   - `orders_admin.py` (CRUD/filters/status transitions/timeline)
   - `carts_admin.py` (abandoned carts list/mark contacted)
   - `users_admin.py` (users list, user detail summary)
   - `upsells_admin.py` (CRUD) + public `GET /api/upsells`
   - `dashboard.py` (KPIs)
   - `router.py` + `__init__.py`
2. Інтегрувати в `server.py` через `app.include_router(build_sales_router(db), prefix="/api")`.
3. Розширити `orders` (optional defaults):
   - `payment_status` (pending/awaiting_confirmation/paid/refunded/failed)
   - `payment_method` (cod/bank_transfer/card)
   - `paid_at`, `paid_amount`, `payment_proof_url`
   - `user_id`, `customer_email`, `customer_name`
   - `internal_status` (new/confirmed/packed/shipped/delivered/cancelled)
   - `tags[]`, `admin_notes[]` (timeline)
4. Abandoned carts:
   - критерій: cart.items!=[] AND no recent order for session_id AND updated_at older than threshold
   - backfill/collect `contact_phone/email` із profile/user (якщо доступно)
5. Dashboard endpoint: revenue/paid counts/users totals/abandoned carts value/top products.

**Frontend (мінімум для адмінки, без редизайну сайту):**
1. Додати `lib/sales-api.ts`.
2. Додати сторінки:
   - `/admin/sales/orders` (table + filters)
   - `/admin/sales/orders/:id` (detail + confirm/refund + proof upload + notes)
   - `/admin/sales/abandoned-carts`
   - `/admin/sales/users`
   - `/admin/sales/upsells`
3. Оновити `AdminLayout` sidebar: нова група “Продажі / CRM”.
4. Оновити `App.tsx` routes.
5. Після імплементації — 1 раунд e2e тестів через testing_agent.

**V1 user stories (5):**
1. Як адмін, я фільтрую замовлення за `payment_status` та `internal_status`.
2. Як адмін, я бачу в замовленні хто оплатив (ПІБ/телефон/email) і method.
3. Як адмін, я бачу список покинутих кошиків з контактами й сумою кошика.
4. Як адмін, я бачу користувачів з total orders та LTV.
5. Як адмін, я створюю upsell правило “A → B” і воно повертається public endpoint.

### Phase 3 — Hardening + Sales Ops (допродаж/ре-консиліація/аудит)
1. Додати “sales events” (payment_confirmed, status_changed, note_added) з audit trail.
2. Додати більш жорсткі правила переходів статусів (state machine).
3. Додати bulk-операції: batch confirm, batch tag, export CSV.
4. Розширити abandoned carts: “assign manager”, “next_contact_at”, “contacted_status”.
5. Розширити dashboard (conversion rate, cohorts, top abandoned products).
6. Повторний e2e тест через testing_agent.

**Hardening user stories (5):**
1. Як адмін, я бачу timeline подій по замовленню (хто/коли змінив статус/оплату).
2. Як менеджер, я фільтрую abandoned carts “не контактували 48h”.
3. Як адмін, я експортую замовлення за період в CSV.
4. Як адмін, я роблю batch tag “priority” для групи замовлень.
5. Як адмін, я бачу conversion rate (кошики→замовлення) за 7/30 днів.

## 3) Next Actions (immediate)
1. Створити `/app/backend/sales/` каркас + router composer.
2. Реалізувати POC endpoints для bank_transfer proof + confirm.
3. Написати скрипт `backend/scripts/sales_poc.py` і прогнати його до успіху.
4. Після green POC — перейти до V1 модулів (orders_admin/carts_admin/users_admin/upsells/dashboard).

## 4) Success Criteria
- POC: bank_transfer order проходить `upload-proof → confirm → paid` (скрипт OK).
- `GET /api/admin/sales/orders` підтримує фільтри, пагінацію, пошук.
- Admin може керувати internal_status/payment_status та бачить контактні дані.
- Abandoned carts і users summaries доступні в адмінці.
- Upsell правила керуються з адмінки і працюють через public endpoint.
- Backend лишається модульним (нові файли в `sales/`, без розростання `server.py`/моноліту).
