import configparser
import redis
from aiogram import Bot, Dispatcher, executor, types
import bot_common
config = configparser.ConfigParser()
config.read('bot.ini')
TOKEN = config["bot"]["tg_token"]
issues_link = "https://github.com/AvaCity/avacity-2.0/issues"

bot = Bot(token=6296239815:AAHWZ_iYhTCVw8OwsASmwPI_R0mnIo5SHDE)
dp = Dispatcher(bot)
r = redis.Redis(decode_responses=True)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply("Cześć!\nTutaj możesz się zarejestrować w AvieOnline! "
                        "Baza kodu źródłowego AvaCity 2.0. Administracja "
                        "tego serwera nie ma nic wspólnego z с AvaCity.\n"
                        "Aby uzyskać hasło, wpisz /password\n"
                        "Zmiana hasła - /change_password\nResetowanie konta - "
                        f"/reset\nWszelkie błędy zgłaszaj w {issues_link}\n"
                        "Miłej gry!")


@dp.message_handler(commands=["password"])
async def password(message: types.Message):
    passwd = r.get(f"tg:{message.from_user.id}")
    if passwd:
        uid = r.get(f"auth:{passwd}")
    else:
        uid, passwd = bot_common.new_account(r)
        r.set(f"tg:{message.from_user.id}", passwd)
    await message.reply(f"Nazwa użytkownika: {uid}\nHasło: {passwd}")


@dp.message_handler(commands=["change_password"])
async def change_password(message: types.Message):
    passwd = r.get(f"tg:{message.from_user.id}")
    if not passwd:
        return await message.reply("Twoje konto nie zostało jeszcze utworzone.")
    while True:
        new_passwd = bot_common.random_string()
        if r.get(f"auth:{new_passwd}"):
            continue
        break
    uid = r.get(f"auth:{passwd}")
    r.delete(f"auth:{passwd}")
    r.set(f"auth:{new_passwd}", uid)
    r.set(f"tg:{message.from_user.id}", new_passwd)
    await message.reply(f"Nowe hasło: {new_passwd}")


@dp.message_handler(commands=["reset"])
async def reset(message: types.Message):
    passwd = r.get(f"tg:{message.from_user.id}")
    if not passwd:
        return await message.reply("Twoje konto nie zostało jeszcze utworzone.")
    uid = r.get(f"auth:{passwd}")
    bot_common.reset_account(r, uid)
    await message.reply(f"Twoje konto zostało zresetowane.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
