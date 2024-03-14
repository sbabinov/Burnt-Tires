async def on_startup(dp):
    from utils.notify_admins import on_startup_notify

    await on_startup_notify(dp)
    print("Бот запущен")

    from utils.set_bot_commands import set_default_commands

    await set_default_commands(dp)


# запуск бота
if __name__ == "__main__":
    from aiogram import executor
    from loader import sdb
    from handlers import dp, all_views

    sdb.update_views(all_views)
    executor.start_polling(dp, on_startup=on_startup)
