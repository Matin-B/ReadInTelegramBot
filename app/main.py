import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize
from pymongo import MongoClient
from pocket import request_auth_code, generate_auth_url, request_auth_access_token
import config

# Configuration logging
logging.basicConfig(level=logging.INFO)

# Initialize bot
bot = Bot(
    token=config.BOT_TOKEN,
    parse_mode=types.ParseMode.HTML,
)
dp = Dispatcher(bot)

# Create MongoDB connection
mongo_client = MongoClient(config.MONGO_URI)

# Connect to MongoDB database
database = mongo_client[config.MONGO_DB]

users_collection = database["users"]
auth_collection = database["auth"]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Create main menu keyboard

    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(
            emojize(":card_index_dividers: My List"),
            callback_data="my_list",
        ),
    )


def back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Create back to main menu keyboard

    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(
            emojize(":house: Main Menu"),
            callback_data="main_menu",
        ),
    )


def get_authentication_status(user_id: int) -> bool:
    """
    Check if user is authenticated

    :param user_id: user id
    :return: True if user is authenticated, False otherwise
    """
    return users_collection.find_one({"_id": user_id})["authentication_status"]


def update_authentication_status(user_id: int, status: bool) -> None:
    """
    Update authentication status

    :param user_id: user id
    :param status: status
    :return: None
    """
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {"authentication_status": status}}
    )


def get_authentication_data(user_id: int) -> dict:
    """
    Get authentication data

    :param user_id: user id
    :return: authentication data
    """
    return auth_collection.find_one({"_id": user_id})


def update_authorization_data(user_id: int, data_name: str, data_value: str) -> None:
    """
    Update authorization data

    :param user_id: user id
    :param data_name: data name
    :param data_value: data value
    :return: None
    """
    auth_collection.update_one(
        {"_id": user_id},
        {"$set": {data_name: data_value}}
    )


def pocket_authenticate(user_id: int) -> None:
    """
    Authenticate user

    :param user_id: user id
    :return: None
    """
    update_authentication_status(user_id, True)


async def delete_message(chat_id, message_id):
    """
    It deletes the message that was replied to in the chat
    
    :param chat_id: The chat ID of the chat where the message will be deleted
    :param message_id: The message id to delete
    """
    await bot.delete_message(chat_id, message_id)


@dp.message_handler(commands=["start"])
async def start_command_handler(message: types.Message):
    """
    Handle /start command
    """
    chat_id = message.chat.id
    message_args = message.get_args()

    user_status = users_collection.find_one({"_id": chat_id})

    if user_status is None:
        users_collection.insert_one({
            "_id": chat_id,
            "authentication_status": False,
        })
        auth_collection.insert_one({
            "_id": chat_id,
            "message_id": None,
            "auth_code": None,
            "auth_url": None,
            "auth_access_token": None,
            "pocket_username": None,
        })

    if len(message_args) != 0 and "authorizationFinished_" in message_args:
        user_id = int(message_args.split("authorizationFinished_")[1])
        if user_id != chat_id:
            await message.reply(
                emojize(
                    "Authorization failed. Please, try again.",
                )
            )
        elif get_authentication_status(user_id):
            await message.reply(
                emojize(
                    "You are already authorized.",
                )
            )
        else:
            authentication_data = get_authentication_data(user_id)
            auth_message_id = authentication_data["message_id"]
            auth_code = authentication_data["auth_code"]
            auth_access_token = request_auth_access_token(auth_code)
            if auth_access_token["status"]:
                username = auth_access_token["username"]
                access_token = auth_access_token["access_token"]

                update_authorization_data(user_id, "auth_access_token", access_token)
                update_authorization_data(user_id, "pocket_username", username)

                update_authentication_status(user_id, True)

                await delete_message(chat_id, auth_message_id)
                await message.reply(
                    emojize(
                        "Authorization successful. You can now use the bot.",
                    )
                )
            else:
                await message.reply(
                    emojize(
                        "Authorization failed. Please, try again.",
                    )
                )
    if get_authentication_status(chat_id):
        await message.reply(
            emojize(
                "Main Menu:"
            ),
            reply_markup=main_menu_keyboard()
        )
    else:
        keyboard = InlineKeyboardMarkup().row(
            InlineKeyboardButton(
                emojize(
                    ":globe_with_meridians: Login via Pocket"
                ),
                callback_data="login"
            )
        )
        await message.reply(
            emojize(
                "Hello! You can use me to get articles from your GetPocket account."
            ),
            reply_markup=keyboard
        )


@dp.callback_query_handler(
    text=["login"]
)
async def login_button_handler(query: types.CallbackQuery):
    """
    Handle login button
    """
    chat_id = query.message.chat.id
    message_id = query.message.message_id

    auth_code = request_auth_code(chat_id)
    if auth_code["status"]:
        code = auth_code["code"]
        auth_url = generate_auth_url(chat_id, code)

        update_authorization_data(chat_id, "auth_code", code)
        update_authorization_data(chat_id, "auth_url", auth_url)
        update_authorization_data(chat_id, "message_id", message_id)

        keyboard = InlineKeyboardMarkup().row(
            InlineKeyboardButton(
                "Authorize Pocket",
                url=auth_url,
            )
        )
        await query.message.edit_text(
            emojize(
                "Please press the button below to connect your Telegram "\
                "account to <a href=\"https://getpocket.com/\">Pocket</a>."
            ),
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    else:
        await query.message.edit_text(
            emojize(
                "Something went wrong :man_facepalming_light_skin_tone:. Please, try again. "
                "if the problem persists, contact the developer."
            )
        )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
