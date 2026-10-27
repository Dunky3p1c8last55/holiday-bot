import logging

from vkbottle import GroupEventType
from vkbottle.bot import Bot, Message, MessageEvent

from app.bot import keyboards
from app.bot.states import BotStates
from app.domain import scenario, texts

logger = logging.getLogger(__name__)

MENU_COMMANDS = [
    "/start", "start",
    "Начать", "начать",
    "Меню", "меню",
    "Назад", "назад",
]

# Простое хранилище настроек в памяти (без БД)
user_settings: dict[int, str] = {}


async def _send_menu(bot: Bot, peer_id: int, text: str) -> None:
    await bot.state_dispenser.set(peer_id, BotStates.MENU)
    await bot.api.messages.send(
        peer_id=peer_id,
        message=text,
        random_id=0,
        keyboard=keyboards.reply_main_menu(),
    )


async def _snackbar(event: MessageEvent, text: str) -> None:
    try:
        await event.show_snackbar(text)
    except Exception as exc:
        logger.debug("snackbar failed: %s", exc)


def get_country(user_id: int) -> str:
    return user_settings.get(user_id, "Россия")


def register_handlers(bot: Bot) -> None:

    @bot.on.message(text=MENU_COMMANDS)
    async def start_handler(message: Message) -> None:
        await _send_menu(bot, message.peer_id, texts.TXT_WELCOME)

    @bot.on.message(text=["Праздники сегодня", "Сегодня", "/today"])
    async def today_handler(message: Message) -> None:
        country = get_country(message.from_id)
        text = scenario.today_text(country)
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        await message.answer(text, keyboard=keyboards.inline_back_to_menu())

    @bot.on.message(text=["Ближайшие 7 дней", "Неделя", "/week"])
    async def week_handler(message: Message) -> None:
        country = get_country(message.from_id)
        text = scenario.week_text(country=country)
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        await message.answer(text, keyboard=keyboards.inline_back_to_menu())

    @bot.on.message(text=["Календарь месяца", "Месяц", "/month"])
    async def month_handler(message: Message) -> None:
        country = get_country(message.from_id)
        text = scenario.month_text(country=country)
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        await message.answer(text, keyboard=keyboards.inline_back_to_menu())

    @bot.on.message(text=["Поиск праздника", "Поиск", "/search"])
    async def search_prompt_handler(message: Message) -> None:
        await bot.state_dispenser.set(message.peer_id, BotStates.WAITING_SEARCH)
        await message.answer(texts.TXT_ASK_SEARCH)

    @bot.on.message(text=["Настройки страны", "Страна", "/country"])
    async def settings_handler(message: Message) -> None:
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        current = get_country(message.from_id)
        await message.answer(
            f"🌍 Текущая страна: {current}\nВыберите новую:",
            keyboard=keyboards.inline_countries(),
        )

    @bot.on.message(text=["Помощь", "/help"])
    async def help_handler(message: Message) -> None:
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        await message.answer(texts.TXT_HELP, keyboard=keyboards.reply_main_menu())

    @bot.on.message(state=BotStates.WAITING_SEARCH)
    async def search_input_handler(message: Message) -> None:
        query = (message.text or "").strip()
        if not query:
            await message.answer(texts.TXT_ASK_SEARCH)
            return

        country = get_country(message.from_id)
        result = scenario.search_holidays(query, country)

        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        await message.answer(result, keyboard=keyboards.inline_search_result())

    @bot.on.message()
    async def fallback_handler(message: Message) -> None:
        await bot.state_dispenser.set(message.peer_id, BotStates.MENU)
        await message.answer(texts.TXT_FALLBACK, keyboard=keyboards.reply_main_menu())

    @bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
    async def callback_handler(event: MessageEvent) -> None:
        payload = event.payload or {}
        cmd = payload.get("cmd")
        peer_id = event.peer_id
        user_id = event.user_id

        if cmd == "menu":
            await _snackbar(event, texts.TXT_MAIN_MENU)
            await _send_menu(bot, peer_id, texts.TXT_WELCOME)

        elif cmd == "set_country":
            country = payload.get("name", "Россия")
            user_settings[user_id] = country
            await _snackbar(event, f"Страна изменена: {country}")
            
            await bot.api.messages.send(
                peer_id=peer_id,
                message=f"✅ Настройки сохранены. Текущая страна: {country}.\nВернитесь в меню, чтобы продолжить.",
                random_id=0,
            )

        elif cmd == "search_again":
            await _snackbar(event, texts.TXT_ASK_SEARCH)
            await bot.state_dispenser.set(peer_id, BotStates.WAITING_SEARCH)
            await bot.api.messages.send(
                peer_id=peer_id,
                message=texts.TXT_ASK_SEARCH,
                random_id=0,
            )
