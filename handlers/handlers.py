from aiogram import Bot, types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import asyncio
from user_data import save_entry, read_user_data
from game_logic import get_random_phrase, get_random_challenge, is_valid_response, in_battle
from ui import get_start_keyboard, get_change_phrase_keyboard
from constants import Command, last_entries, battles, current_phrases
from utils.utilities import clean_html_tags
from handlers.callback_handlers import handle_play, handle_change_phrase, handle_show_example, handle_back_to_main, handle_add_challenge, handle_battle, handle_start_battle
from leaderboards import generate_leaderboard

router = Router()
battle_data = battles[list(battles.keys())[0]] if battles else {}
bot = Bot(token='722571834:AAEks8GjnDZUmaHbBP5RCQz9At8t9__82BA')

@router.callback_query()
async def callback_query_handler(query: CallbackQuery):
    global battle_data
    data = query.data
    user_id = query.from_user.id
    print(f"[DEBUG] Callback query data received: {data}")

    # Fetch the user data from CSV
    user_data = read_user_data()

    handlers = {
        Command.PLAY.value: handle_play,
        Command.BATTLE.value: handle_battle,
        Command.CHANGE_PHRASE.value: handle_change_phrase,
        Command.SHOW_EXAMPLE.value: handle_show_example,
        Command.HELP.value: lambda q, uid: q.message.answer("You pressed Help!"),
        Command.LEADERBOARD.value: lambda q, uid: q.message.answer(generate_leaderboard()),
        Command.ADD_CHALLENGE.value: handle_add_challenge,
        Command.START_BATTLE.value: handle_start_battle,
    }

    handler = handlers.get(data.split(":", 1)[0], None)

    print(f"[DEBUG] Callback query data received: {data}")

    if handler:
        await handler(query, user_id)
    elif Command.BACK_TO_MAIN.value in data:
        await handle_back_to_main(query, user_id)
    else:
        await query.message.answer("Unknown button!")

@router.message()
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    username = msg.from_user.full_name

    print(f"[DEBUG] User Message: {msg.text}")
    print(f"[DEBUG] User ID: {user_id}")
    print(f"[DEBUG] Chat ID: {chat_id}")
    print(f"[DEBUG] Current battles state: {battles}")
    print(f"[DEBUG] Current phrases state: {current_phrases}")

    battles.setdefault(chat_id, {})
    battles[chat_id].setdefault("participants", {})

    if chat_id not in current_phrases:
        current_phrases[chat_id] = (None, None)

    entry_data, is_challenge = current_phrases.get(chat_id)
    print(f"[DEBUG] is_challenge: {is_challenge}")

    if entry_data is None:
        keyboard = get_start_keyboard()
        await msg.answer("First, press 'Play' to get a phrase!", reply_markup=keyboard, parse_mode='HTML')
        return

    if is_challenge:
        challenge_number, challenge_text = entry_data
        cleaned_challenge = clean_html_tags(challenge_text)
    else:
        cleaned_challenge = clean_html_tags(entry_data)

    user_response = msg.text.strip()
    print(f"[DEBUG] user_response: {user_response}")
    print(f"[DEBUG] cleaned_challenge: {cleaned_challenge}")

    if is_valid_response(user_response, cleaned_challenge, is_challenge):
        print("[DEBUG] is_valid_response returned True.")
        if user_id not in battles[chat_id]["participants"]:
            battles[chat_id]["participants"][user_id] = {"score": 0, "responses": []}

        battles[chat_id]["participants"][user_id]["score"] += 1
        battles[chat_id]["participants"][user_id]["responses"].append(user_response)
        battles[chat_id]["participants"][user_id]["full_name"] = username
        print(f"[DEBUG] Updated battles: {battles}")

        new_phrase = get_random_phrase()
        current_phrases[chat_id] = (new_phrase, False)
        keyboard = get_change_phrase_keyboard()

        current_phrase_message_id = battles[chat_id].get('current_phrase_message_id')
        if current_phrase_message_id:
            try:
                await bot.edit_message_reply_markup(chat_id=chat_id, message_id=current_phrase_message_id)
            except TelegramBadRequest as e:
                print(f"TelegramBadRequest while deleting buttons: {e}")

        sent_message = await msg.answer(new_phrase, reply_markup=keyboard, parse_mode='HTML')
        battles[chat_id]['current_phrase_message_id'] = sent_message.message_id

        score = 2 if is_challenge else 1
        battles[chat_id]["participants"][user_id]["score"] += score

        print(f"[DEBUG] score: {score}")

        if is_challenge:
            phrase_from_user_reply = user_response.split()[0]
            save_entry(username, phrase_from_user_reply, user_response, score=score, challenge_number=challenge_number)
        else:
            save_entry(username, current_phrase=cleaned_challenge, user_message=user_response, score=score)

        print(f"[DEBUG] Participants after: {battles[chat_id]['participants']}")

    else:
        print("[DEBUG] is_valid_response returned False.")
        if chat_id in battles:
            await msg.answer("No, that's not a valid answer.")
        else:
            play_keyboard = get_start_keyboard()
            await msg.answer("Game Over! Try again by pressing 'Play'.", reply_markup=play_keyboard)


