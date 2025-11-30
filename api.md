# Real Estate Tinder API

Backend для сервиса по аренде/продаже недвижимости с “тиндер-подбором” объектов.

- **Dev base URL (локально):** `http://localhost:8000`
- **Prod base URL (GCP):** `http://<SERVER_IP>:8000`
- **Формат:** JSON
- **Авторизация:** `Authorization: Bearer <access_token>`

---

## 🔐 Auth

### POST `/auth/register`

Регистрация пользователя.

**Auth:** не требуется.

**Body:**

```json
{
  "role": "tenant",           // tenant | landlord | agent
  "name": "Имя Фамилия",
  "email": "user@example.com",
  "phone": "+77001234567",
  "password": "secret123"
}
Response 200:

json
Copy code
{
  "id": 2,
  "role": "tenant",
  "name": "Имя Фамилия",
  "email": "user@example.com",
  "phone": "+77001234567",
  "telegram_id": null,
  "is_active": true,
  "created_at": "2025-11-30T12:00:00Z"
}
POST /auth/login
Логин по email или телефону, возвращает JWT.

Auth: не требуется.
Content-Type: application/x-www-form-urlencoded

Body:

text
Copy code
username=user@example.com  // или +77001234567
password=secret123
Response 200:

json
Copy code
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
Токен сохраняется на фронте и передаётся в заголовке:

http
Copy code
Authorization: Bearer <JWT>
GET /auth/me
Текущий пользователь по токену.

Auth: Bearer <token>

Response 200:

json
Copy code
{
  "id": 2,
  "role": "tenant",
  "name": "Имя Фамилия",
  "email": "user@example.com",
  "phone": "+77001234567",
  "telegram_id": "123456789",
  "is_active": true,
  "created_at": "2025-11-30T12:00:00Z"
}
POST /auth/telegram/login-or-register
Спец-эндпоинт для Telegram-бота.

Логика:

Ищем пользователя по telegram_id.

Если нет — ищем по phone и привязываем telegram_id к существующему пользователю.

Если всё равно нет — создаём нового пользоватeля.

Auth: не требуется.

Body:

json
Copy code
{
  "telegram_id": "123456789",
  "phone": "+77001234567",
  "name": "Имя из Telegram",
  "role": "tenant"
}
Response 200:

json
Copy code
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
Используется ботом, не фронтом.

👤 Роли пользователей
Поле role в сущности пользователя:

tenant — арендатор

landlord — арендодатель (владелец)

agent — агент/риелтор

admin — администратор системы

Фронт показывает разные экраны/разделы в зависимости от роли.

🏠 Объявления (Listings)
Общий формат объявления (ListingRead):

json
Copy code
{
  "id": 1,
  "title": "Квартира в Астане",
  "city": "Astana",
  "deal_type": "rent",       // rent | sale
  "property_type": "flat",   // flat | house | room | commercial
  "price": "250000.00",
  "is_active": true,
  "owner_id": 3,
  "created_at": "2025-11-30T12:27:33.197286Z",
  "updated_at": "2025-11-30T12:27:33.197286Z"
}
POST /listings
Создать объявление.
Владелец (owner_id) берётся из текущего пользователя.

Auth: Bearer <token>

Body:

json
Copy code
{
  "title": "Квартира в Астане",
  "city": "Astana",
  "deal_type": "rent",
  "property_type": "flat",
  "price": 250000,
  "is_active": true
}
Response 200: ListingRead.

GET /listings
Публичный список активных объявлений.

Auth: не требуется.

Query-параметры:

city — опционально

Пример:

http
Copy code
GET /listings?city=Astana
Response 200:

json
Copy code
[
  { ...ListingRead },
  { ...ListingRead }
]
GET /listings/{id}
Детальная информация по объявлению.

Auth: не требуется.

Response 200: ListingRead
404: если не найдено или is_active = false.

GET /listings/my
Список объявлений текущего пользователя (владелец/агент).

Auth: Bearer <token>

Response 200:

json
Copy code
[
  { ...ListingRead },
  ...
]
PUT /listings/{id}
Обновить объявление.

Кто: владелец объявления или admin.
Auth: Bearer <token>

Body: такие же поля, как при создании:

json
Copy code
{
  "title": "Новое название",
  "city": "Astana",
  "deal_type": "rent",
  "property_type": "flat",
  "price": 260000,
  "is_active": true
}
Response 200: обновлённый ListingRead.

DELETE /listings/{id}
Мягкое удаление (установка is_active = false).

Кто: владелец или admin.
Auth: Bearer <token>

Response 200:

json
Copy code
{ "status": "ok" }
🎯 Предпочтения арендатора (Preferences)
Используются для подбора объектов в “ленты”.

Формат (TenantPreferenceRead):

json
Copy code
{
  "id": 1,
  "user_id": 2,
  "city": "Astana",
  "deal_type": "rent",
  "property_type": "flat",
  "price_min": 100000,
  "price_max": 400000
}
GET /preferences
Получить предпочтения текущего пользователя.

Auth: Bearer <token>

Response 200:

либо объект, как выше,

либо null, если ещё не задавали.

POST /preferences
Создать или обновить предпочтения текущего пользователя.

Auth: Bearer <token>

Body:

json
Copy code
{
  "city": "Astana",
  "deal_type": "rent",
  "property_type": "flat",
  "price_min": 100000,
  "price_max": 400000
}
Response 200: объект предпочтений.

🧩 Лента (Feed, “тиндер” по объявлениям)
GET /feed/next
Получить следующее объявление для текущего пользователя с учётом:

его предпочтений

уже просмотренных/лайкнутых/дизлайкнутых объявлений

Auth: Bearer <token>

Response 200:

ListingRead — если есть подходящий объект,

null — если всё просмотрено.

POST /feed/action
Сохранить действие пользователя по объявлению.

Действия:

like

dislike

favorite

Побочные эффекты:

like → создаётся Lead (если его ещё нет)

favorite → добавляет в избранное

Auth: Bearer <token>

Body:

json
Copy code
{
  "listing_id": 1,
  "action": "like",       // like | dislike | favorite
  "source": "web"         // web | telegram | ...
}
Response 200:

json
Copy code
{ "status": "ok" }
⭐ Избранное (Favorites)
GET /favorites/
Список объявлений в избранном у текущего пользователя.

Auth: Bearer <token>

Response 200:

json
Copy code
[
  { ...ListingRead },
  ...
]
POST /favorites/
Добавить объявление в избранное текущего пользователя.

Auth: Bearer <token>

Body:

json
Copy code
{
  "listing_id": 1
}
Response 200:

json
Copy code
{
  "id": 1,
  "user_id": 2,
  "listing_id": 1,
  "created_at": "2025-11-30T12:00:00Z"
}
DELETE /favorites/{listing_id}
Удалить объявление из избранного текущего пользователя.

Auth: Bearer <token>

Response 200:

json
Copy code
{ "status": "ok" }
📩 Leads (лиды/заявки)
Лид создаётся автоматически при action = like в /feed/action, либо вручную.

Формат (LeadRead):

json
Copy code
{
  "id": 1,
  "tenant_id": 2,
  "listing_id": 1,
  "owner_id": 3,
  "status": "new",        // new | in_progress | closed
  "created_at": "2025-11-30T12:30:03.362734Z"
}
GET /leads/my
Лиды, где текущий пользователь — арендатор (он лайкнул объявления).

Auth: Bearer <token>

Response 200: LeadRead[]

GET /leads/for-me
Лиды по объявлениям текущего пользователя (владелец/агент).

Кто: landlord | agent | admin
Auth: Bearer <token>

Response 200: LeadRead[]

POST /leads/
Ручное создание лида (обычно не нужно фронту, достаточно /feed/action).

Auth: Bearer <token>

Body:

json
Copy code
{
  "listing_id": 1,
  "owner_id": 3,
  "status": "new"
}
Response 200: LeadRead.

🛠 Admin API
Доступно только пользователю с role = "admin".

GET /admin/users
Список всех пользователей.

Auth: Bearer <admin_token>

Response 200:

json
Copy code
[
  {
    "id": 2,
    "name": "Имя",
    "role": "tenant",
    "email": "user@example.com",
    "phone": "+7700...",
    "is_active": true,
    "created_at": "2025-11-30T12:00:00Z"
  }
]
PATCH /admin/users/{user_id}
Обновить роль/активность пользователя.

Auth: Bearer <admin_token>

Body:

json
Copy code
{
  "role": "agent",      // опционально
  "is_active": false    // опционально
}
Response 200: тот же формат, что в списке пользователей.

GET /admin/listings
Список объявлений (включая неактивные) с фильтрами.

Auth: Bearer <admin_token>

Query-параметры (опционально):

city

owner_id

is_active (true / false)

Response 200:

json
Copy code
[
  {
    "id": 1,
    "title": "Квартира",
    "city": "Astana",
    "deal_type": "rent",
    "property_type": "flat",
    "price": 250000,
    "is_active": true,
    "owner_id": 3,
    "created_at": "2025-11-30T12:27:33.197286Z"
  }
]
❤️ Health check
GET /health
Проверка, что сервис жив.

Auth: не требуется.

Response 200:

json
Copy code
{
  "status": "ok",
  "environment": "local"
}