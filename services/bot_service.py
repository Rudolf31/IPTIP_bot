from config import TOKEN

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from services.user_service import UserService
from services.employee_service import EmployeeService


# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if not await UserService.isUserRegistered(message.from_user):
        await UserService.userRegister(message.from_user)

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

@dp.message(Command("employees"))
async def get_employees_handler(message: Message) -> None:
    employees_list = await EmployeeService.getEmployeeList()
    formatted_list = "\n".join(employees_list)
    await message.answer(formatted_list)

@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender
    By default, message handler will handle all message types.
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def run_bot() -> None:
    # Initialize Bot instance with default bot properties
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # And the run events dispatching
    await dp.start_polling(bot)
