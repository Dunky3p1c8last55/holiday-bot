from vkbottle import Callback, Keyboard, KeyboardButtonColor, Text


def reply_main_menu() -> str:
    kb = Keyboard(one_time=False, inline=False)
    kb.add(Text("Праздники сегодня"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("Ближайшие 7 дней"), color=KeyboardButtonColor.SECONDARY)
    kb.row()
    kb.add(Text("Календарь месяца"), color=KeyboardButtonColor.SECONDARY)
    kb.add(Text("Поиск праздника"), color=KeyboardButtonColor.SECONDARY)
    kb.row()
    kb.add(Text("Настройки страны"), color=KeyboardButtonColor.SECONDARY)
    kb.add(Text("Помощь"), color=KeyboardButtonColor.SECONDARY)
    return kb.get_json()


def inline_back_to_menu() -> str:
    kb = Keyboard(one_time=False, inline=True)
    kb.add(Callback("В меню", {"cmd": "menu"}), color=KeyboardButtonColor.SECONDARY)
    return kb.get_json()


def inline_search_result() -> str:
    kb = Keyboard(one_time=False, inline=True)
    kb.add(Callback("Другой поиск", {"cmd": "search_again"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Callback("В меню", {"cmd": "menu"}), color=KeyboardButtonColor.SECONDARY)
    return kb.get_json()


def inline_countries() -> str:
    kb = Keyboard(one_time=False, inline=True)
    kb.add(Callback("Россия", {"cmd": "set_country", "name": "Россия"}))
    kb.add(Callback("Германия (Гессен)", {"cmd": "set_country", "name": "Германия (Гессен)"}))
    return kb.get_json()
