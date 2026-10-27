
import asyncio
import ssl
import certifi
import aiohttp


async def main():
    context = ssl.create_default_context(
        cafile=certifi.where()
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.vk.ru",
                ssl=context,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                print("Соединение установлено!")
                print("HTTP-код:", response.status)

    except Exception as error:
        print("Ошибка подключения:", repr(error))


if __name__ == "__main__":
    asyncio.run(main())
