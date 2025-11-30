import asyncio
from typing import Any, Dict, Optional



from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from . import config
from .api_client import BackendClient
from .token_store import get_token, set_token

# ---------- Глобальные объекты ----------

bot: Bot  # инициализируем в main()
dp: Dispatcher = Dispatcher()  # <--- ВАЖНО: создаём dp сразу
backend: Optional[BackendClient] = None  # создадим в main()


# ---------- Вспомогалки ----------

def build_contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер", request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def listing_to_text(listing: Dict[str, Any]) -> str:
    title = listing.get("title") or "Объект"
    city = listing.get("city") or "-"
    deal_type = listing.get("deal_type") or "-"
    property_type = listing.get("property_type") or "-"
    price = listing.get("price") or "-"

    return (
        f"🏠 <b>{title}</b>\n"
        f"📍 Город: <b>{city}</b>\n"
        f"📑 Сделка: <b>{deal_type}</b>\n"
        f"🏗 Тип: <b>{property_type}</b>\n"
        f"💰 Цена: <b>{price}</b>\n"
    )


def build_listing_keyboard(listing_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❤️ Нравится",
                    callback_data=f"like:{listing_id}",
                ),
                InlineKeyboardButton(
                    text="✖ Пропустить",
                    callback_data=f"dislike:{listing_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⭐ В избранное",
                    callback_data=f"favorite:{listing_id}",
                )
            ],
        ]
    )


async def ensure_token_for_user(message: Message) -> Optional[str]:
    tg_id = message.from_user.id
    token = get_token(tg_id)
    if token:
        return token

    await message.answer(
        "Сначала нужно зарегистрироваться. "
        "Нажми кнопку ниже и отправь свой номер телефона 👇",
        reply_markup=build_contact_keyboard(),
    )
    return None


async def send_next_listing(chat_id: int, tg_user_id: int) -> None:
    global backend
    if backend is None:
        await bot.send_message(chat_id, "Сервис временно недоступен.")
        return

    token = get_token(tg_user_id)
    if not token:
        await bot.send_message(
            chat_id,
            "Токен не найден. Нажми /start и отправь номер ещё раз.",
        )
        return

    listing = await backend.get_next_listing(token)
    if not listing:
        await bot.send_message(
            chat_id,
            "Подходящих объявлений больше нет. Попробуй изменить фильтры на сайте.",
        )
        return

    text = listing_to_text(listing)
    kb = build_listing_keyboard(listing["id"])
    await bot.send_message(chat_id, text, reply_markup=kb)


# ---------- Handlers ----------

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    tg_user = message.from_user
    await message.answer(
        f"Привет, {tg_user.first_name or 'друг'}! 👋\n\n"
        "Я помогу подобрать жильё.\n"
        "Для начала отправь свой номер телефона, чтобы мы тебя идентифицировали.",
        reply_markup=build_contact_keyboard(),
    )


@dp.message(F.contact)
async def contact_received(message: Message) -> None:
    global backend
    if backend is None:
        await message.answer("Сервис временно недоступен, попробуй чуть позже.")
        return

    if not message.contact:
        return

    contact = message.contact
    phone = contact.phone_number
    tg_id = message.from_user.id
    name = message.from_user.full_name

    try:
        token = await backend.login_or_register_telegram(
            telegram_id=tg_id,
            phone=phone,
            name=name,
        )
    except Exception as e:
        await message.answer(
            "Не удалось зарегистрировать/авторизовать тебя 😔\n"
            "Попробуй позже или свяжись с поддержкой.",
            reply_markup=ReplyKeyboardRemove(),
        )
        print("auth error:", e)
        return

    set_token(tg_id, token)

    await message.answer(
        "Готово! ✅\n\n"
        "Теперь можешь искать жильё командой /search.\n"
        "Также доступны:\n"
        "/favorites — избранное\n"
        "/leads — твои отклики",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Command("search"))
async def cmd_search(message: Message) -> None:
    token = await ensure_token_for_user(message)
    if not token:
        return
    await send_next_listing(message.chat.id, message.from_user.id)


@dp.message(Command("favorites"))
async def cmd_favorites(message: Message) -> None:
    global backend
    if backend is None:
        await message.answer("Сервис временно недоступен.")
        return

    token = await ensure_token_for_user(message)
    if not token:
        return

    try:
        favorites = await backend.get_favorites(token)
    except Exception as e:
        await message.answer("Не удалось получить избранное 😔")
        print("favorites error:", e)
        return

    if not favorites:
        await message.answer("У тебя пока нет избранных объявлений ⭐")
        return

    text_parts = [listing_to_text(listing) for listing in favorites[:5]]

    await message.answer(
        "⭐ <b>Твои избранные объекты:</b>\n\n" + "\n".join(text_parts)
    )


@dp.message(Command("leads"))
async def cmd_leads(message: Message) -> None:
    global backend
    if backend is None:
        await message.answer("Сервис временно недоступен.")
        return

    token = await ensure_token_for_user(message)
    if not token:
        return

    try:
        leads = await backend.get_my_leads(token)
    except Exception as e:
        await message.answer("Не удалось получить список твоих откликов 😔")
        print("leads error:", e)
        return

    if not leads:
        await message.answer("Пока нет ни одного отклика (лайка) 👍")
        return

    await message.answer(f"У тебя {len(leads)} откликов на объявления.")


@dp.callback_query(F.data.startswith(("like:", "dislike:", "favorite:")))
async def on_feed_action(callback: CallbackQuery) -> None:
    global backend
    if backend is None:
        await callback.answer("Сервис временно недоступен", show_alert=True)
        return

    tg_id = callback.from_user.id
    token = get_token(tg_id)
    if not token:
        await callback.answer("Нужно заново авторизоваться через /start", show_alert=True)
        return

    try:
        action, listing_id_str = callback.data.split(":", 1)
        listing_id = int(listing_id_str)
    except Exception:
        await callback.answer("Некорректные данные", show_alert=True)
        return

    try:
        await backend.send_feed_action(
            token=token,
            listing_id=listing_id,
            action=action,
            source="telegram",
        )
    except Exception as e:
        print("feed_action error:", e)
        await callback.answer("Ошибка при сохранении действия", show_alert=True)
        return

    next_listing = await backend.get_next_listing(token)

    if not next_listing:
        await callback.message.edit_text(
            "Больше нет подходящих объявлений. "
            "Попробуй позже или измени фильтры на сайте.",
        )
        await callback.answer("Действие сохранено")
        return

    new_text = listing_to_text(next_listing)
    new_kb = build_listing_keyboard(next_listing["id"])

    await callback.message.edit_text(new_text, reply_markup=new_kb)
    await callback.answer("Действие сохранено")


# ---------- entrypoint ----------

async def main() -> None:
    global bot, backend

    bot = Bot(
    token=config.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)

    backend = BackendClient(config.BACKEND_BASE_URL)

    try:
        await dp.start_polling(bot)
    finally:
        await backend.close()


if __name__ == "__main__":
    asyncio.run(main())
