from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

import asyncio

from user_data import save_entry, read_user_data
from game_logic import get_random_phrase, get_random_challenge, is_valid_response, in_battle
from ui import get_start_keyboard, get_change_phrase_keyboard

from constants import Command, last_entries, battles
from utils.utilities import clean_html_tags
from handlers.callback_handlers import handle_play, handle_change_phrase, handle_show_example, handle_back_to_main, handle_add_challenge, handle_battle, handle_start_battle
from leaderboards import generate_leaderboard

router = Router()

battle_data = battles[list(battles.keys())[0]] if battles else {}

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

    if handler:
        await handler(query, user_id)
    elif Command.BACK_TO_MAIN.value in data:
        await handle_back_to_main(query, user_id)
    else:
        await query.message.answer("Unknown button!")

@router.message()
async def message_handler(msg: Message):
    global battle_data
    user_id = msg.from_user.id
    username = msg.from_user.full_name
    
    print(f"[DEBUG] User Message: {msg.text}")
    
    if user_id not in last_entries:
        keyboard = get_start_keyboard()
        await msg.answer("First, press 'Play' to get a phrase!", reply_markup=keyboard, parse_mode='HTML')
        return

    entry_data, is_challenge = last_entries[user_id]

    if is_challenge:
        challenge_number, challenge_text = entry_data
        cleaned_challenge = clean_html_tags(challenge_text)
    else:
        cleaned_challenge = clean_html_tags(entry_data)  # In this case, entry_data is just the phrase

    user_response = msg.text.strip()

    print(f"[DEBUG] Cleaned Challenge: {cleaned_challenge}")

    if is_challenge:
        phrase_from_user_reply = user_response.split()[0]  # Extracting the first word from user's reply
        save_entry(username, phrase_from_user_reply, user_response, score=1, challenge_number=challenge_number)

        new_phrase = get_random_phrase()
        last_entries[user_id] = (new_phrase, False)
        keyboard = get_change_phrase_keyboard()
        await msg.answer(new_phrase, reply_markup=keyboard, parse_mode='HTML')
    else:
        if user_response.lower() == cleaned_challenge.lower():
            print(f"[DEBUG] User's response matched exactly with the challenge.")
            await msg.answer("<b>Good Try, but No</b>", parse_mode='HTML')
            return

        if is_valid_response(user_response, cleaned_challenge):
            # Check if there's an ongoing battle
            for battle_id, battle_data in battles.items():
                if (asyncio.get_event_loop().time() - battle_data["start_time"]) < 180:  # If the battle is still ongoing
                    if user_id not in battle_data["participants"]:
                        battle_data["participants"][user_id] = {
                            "score": 0,
                            "responses": [],
                        }
                # Always update the full name (moved outside the if condition)
                battle_data["participants"][user_id]["full_name"] = msg.from_user.full_name

# Add score and response to the user's data in the battle
            battle_data["participants"][user_id]["score"] += 1  # Assuming each valid response adds 1 point
            battle_data["participants"][user_id]["responses"].append(user_response)
            new_phrase = get_random_phrase()
            last_entries[user_id] = (new_phrase, False)
            keyboard = get_change_phrase_keyboard()
            await msg.answer(new_phrase, reply_markup=keyboard, parse_mode='HTML')
            
            score = 2 if is_challenge else 1
            save_entry(username, current_phrase=cleaned_challenge, user_message=user_response, score=1)
        else:
            play_keyboard = get_start_keyboard()
            await msg.answer("Game Over! Try again by pressing 'Play'.", reply_markup=play_keyboard)
