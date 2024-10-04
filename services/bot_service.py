import logging

from config import TOKEN, ADMINS

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message

from services.user_service import UserService
from services.employee_service import EmployeeService
from services.subscription_service import SubscriptionService
from services.distribution_service import DistributionService
from services.translation_service import TranslationService as TS
from database.controllers.employee_controller import EmployeeController


logger = logging.getLogger(__name__)

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

locale_ru = TS.getTranslation("ru")


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if not await UserService.isUserRegistered(message.from_user):
        await UserService.userRegister(message.from_user)

    message_text = TS.getTemplate(locale_ru, "start")
    await message.answer(message_text.format(name=f"{html.bold(message.from_user.full_name)}"))


@dp.message(Command("test"))
async def Answer(message: Message, command: CommandObject) -> None:
    """
    Function for testing development features.
    Only admin users are able to interact with it.
    Features are not meant to stay forever.
    """
    if message.from_user.id not in ADMINS:
        await message.answer("Only admins are allowed to run tests.")
        return

    if command.args is None:
        await message.answer("Args are missing.")
        return

    cmd = command.args.split()

    try:
        if cmd[0] == "happybd":
            """
            Broadcast notification about employee with id N
            """
            employee = await EmployeeController.getEmployeeById(int(cmd[1]))
            await DistributionService.broadcastBirthdayNotification(employee)
            return
    except Exception as e:
        logger.exception(f"Test failed: {e}")
        await message.answer(f"Test failed: {e}")
        return

    await message.answer("Unknown test.")
    return


@dp.message(Command("subscribe"))
async def subscribe_handler(message: Message) -> None:
    await SubscriptionService.setUserSubscriptionState(message.from_user.id, state=True)

    message_text = TS.getTemplate(locale_ru, "subscribe")
    await message.answer(message_text)


@dp.message(Command("unsubscribe"))
async def unsubscribe_handler(message: Message) -> None:
    await SubscriptionService.setUserSubscriptionState(message.from_user.id, state=False)

    message_text = TS.getTemplate(locale_ru, "unsubscribe")
    await message.answer(message_text)


@dp.message(Command("employees"))
async def get_employees_handler(message: Message) -> None:
    employees_list = await EmployeeService.getEmployeeList()
    formatted_list = "\n".join(employees_list)

    message_text = TS.getTemplate(locale_ru, "employees")
    await message.answer(f"{message_text}\n{formatted_list}")


async def run_bot() -> None:
    global bot

    # And the run events dispatching
    await dp.start_polling(bot)
