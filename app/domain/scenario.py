from datetime import date, timedelta
from difflib import SequenceMatcher
import re
import holidays

COUNTRIES = {
    "Россия": ("RU", None),
    "Германия (Гессен)": ("DE", "HE"),
}

EXTRA_HOLIDAYS = [
    (1, 1, "Новый год", ["новый год", "1 января"]),
    (1, 7, "Рождество Христово", ["рождество", "рождество христово"]),
    (1, 14, "Старый Новый год", ["старый новый год"]),
    (2, 14, "День святого Валентина", ["день валентина", "день всех влюблённых", "день всех влюбленных", "14 февраля"]),
    (2, 23, "День защитника Отечества", ["23 февраля", "день защитника"]),
    (3, 8, "Международный женский день", ["8 марта", "женский день", "международный женский день"]),
    (4, 1, "День смеха", ["1 апреля", "день дурака", "день смеха"]),
    (4, 12, "День космонавтики", ["12 апреля", "день космонавтики"]),
    (5, 1, "Праздник Весны и Труда", ["1 мая", "первое мая", "день труда"]),
    (5, 9, "День Победы", ["9 мая", "день победы"]),
    (6, 1, "Международный день защиты детей", ["1 июня", "день защиты детей"]),
    (6, 12, "День России", ["12 июня", "день россии"]),
    (7, 8, "День семьи, любви и верности", ["8 июля", "день семьи", "день любви и верности"]),
    (9, 1, "День знаний", ["1 сентября", "день знаний"]),
    (10, 5, "День учителя", ["5 октября", "день учителя"]),
    (10, 31, "Хэллоуин", ["хэллоуин", "halloween", "31 октября"]),
    (11, 4, "День народного единства", ["4 ноября", "народного единства"]),
    (12, 12, "День Конституции Российской Федерации", ["12 декабря", "день конституции"]),
    (12, 31, "Канун Нового года", ["31 декабря", "канун нового года"]),
]


def _holiday_calendar(year: int, country: str = "Россия"):
    if holidays is None:
        return {}
    code, subdivision = COUNTRIES.get(country, ("RU", None))
    kwargs = {"country": code, "years": year}
    if subdivision:
        kwargs["subdiv"] = subdivision
    try:
        return holidays.country_holidays(**kwargs)
    except Exception:
        return {}


def describe_day(day: date, country: str = "Россия") -> str:
    name = _holiday_calendar(day.year, country).get(day)
    if name:
        return f"🎉 Государственный праздник: {name}"
    if day.weekday() == 5:
        return "🟣 Суббота — выходной день"
    if day.weekday() == 6:
        return "🟣 Воскресенье — выходной день"
    return "💼 Обычный рабочий день"


def today_text(country: str = "Россия") -> str:
    today = date.today()
    return (
        f"💜 Сегодня — {today:%d.%m.%Y}\n"
        f"{describe_day(today, country)}"
    )


def week_text(start: date | None = None, country: str = "Россия") -> str:
    start = start or date.today()
    lines = ["📅 Ближайшие 7 дней"]
    for offset in range(7):
        day = start + timedelta(days=offset)
        lines.append(f"• {day:%d.%m.%Y} — {describe_day(day, country)}")
    return "\n".join(lines)


def month_text(year: int | None = None, month: int | None = None, country: str = "Россия") -> str:
    from calendar import monthrange
    today = date.today()
    year = year or today.year
    month = month or today.month
    lines = [f"🗓 Праздники и выходные — {month:02d}.{year}"]
    for n in range(1, monthrange(year, month)[1] + 1):
        day = date(year, month, n)
        desc = describe_day(day, country)
        if desc.startswith("🎉") or day.weekday() >= 5:
            lines.append(f"• {day:%d.%m.%Y} — {desc}")
    if len(lines) == 1:
        lines.append("В этом месяце нет найденных праздников или выходных.")
    return "\n".join(lines)


def _normalize_holiday_text(value: str) -> str:
    value = value.casefold().replace("ё", "е")
    value = re.sub(r"[^\w\s]", " ", value)
    return " ".join(value.split())


def search_holidays(query: str, country: str = "Россия") -> str:
    query = _normalize_holiday_text(query)

    if not query:
        return "Напишите название праздника, который нужно найти."

    today = date.today()
    years = range(today.year, today.year + 6)
    found = {}

    # 1. Ищем официальные праздники в библиотеке holidays.
    try:
        code, subdivision = COUNTRIES.get(country, ("RU", None))
        kwargs = {"country": code, "years": years}
        if subdivision:
            kwargs["subdiv"] = subdivision
        calendar = holidays.country_holidays(**kwargs)

        for holiday_date, holiday_name in calendar.items():
            name = str(holiday_name)
            normalized_name = _normalize_holiday_text(name)

            if query in normalized_name or normalized_name in query:
                found[(holiday_date, name)] = f"📅 {holiday_date:%d.%m.%Y} — {name}"
            else:
                similarity = SequenceMatcher(None, query, normalized_name).ratio()
                if len(query) >= 5 and similarity >= 0.82:
                    found[(holiday_date, name)] = f"📅 {holiday_date:%d.%m.%Y} — {name}"
    except Exception:
        pass

    # 2. Ищем дополнительные популярные праздники.
    for month, day, name, aliases in EXTRA_HOLIDAYS:
        searchable_names = [name] + aliases
        matched = any(
            query in _normalize_holiday_text(item) or _normalize_holiday_text(item) in query
            for item in searchable_names
        )
        if not matched:
            matched = any(
                len(query) >= 5
                and SequenceMatcher(None, query, _normalize_holiday_text(item)).ratio() >= 0.82
                for item in searchable_names
            )
        if matched:
            for year in years:
                try:
                    holiday_date = date(year, month, day)
                except ValueError:
                    continue
                found[(holiday_date, name)] = f"📅 {holiday_date:%d.%m.%Y} — {name}"

    if not found:
        return (
            f"🔎 По запросу «{query}» праздник не найден.\n\n"
            "Попробуйте написать короткую часть названия или другое название праздника."
        )

    results = sorted(found.items(), key=lambda item: item[0][0])
    results = [item for item in results if item[0][0] >= today][:15]

    if not results:
        return (
            "Праздник найден, но ближайшие даты не попали в период поиска. "
            "Попробуйте повторить поиск позже."
        )

    lines = [
        f"🎉 Результаты поиска: {len(results)}",
        "",
        *[item[1] for item in results],
        "",
        "Показаны даты на ближайшие годы.",
    ]

    return "\n".join(lines)
