from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from game_logic import get_random_phrase, get_random_challenge, start_battle
from ui import get_change_phrase_keyboard, get_battle_start_keyboard, get_battle_end_keyboard, get_start_keyboard
from utils.utilities import clean_html_tags
from user_data import read_user_data
from constants import last_entries, battles
import asyncio  # New import
import uuid

import random

async def handle_play(query, user_id):
    phrase = get_random_phrase()
    last_entries[user_id] = (phrase, False)
    keyboard = get_change_phrase_keyboard()
    await query.message.answer(phrase, reply_markup=keyboard, parse_mode='HTML')

async def handle_change_phrase(query, user_id):
    new_phrase = get_random_phrase()
    last_entries[user_id] = (new_phrase, False)
    keyboard = get_change_phrase_keyboard()
    await query.message.edit_text(new_phrase, reply_markup=keyboard, parse_mode='HTML')

async def handle_add_challenge(query, user_id):
    challenge_number, challenge_text = get_random_challenge()
    last_entries[user_id] = ((challenge_number, challenge_text), True)
    await query.message.answer(challenge_text, parse_mode='HTML')

async def handle_show_example(query, user_id):
    print("[DEBUG] Entered handle_show_example function.")

    if user_id not in last_entries:
        print("[DEBUG] User does not have an active phrase.")
        await query.message.answer("No active phrase to show examples for!")
        return

    current_phrase = clean_html_tags(last_entries[user_id][0]) if not last_entries[user_id][1] else None
    print(f"[DEBUG] Cleaned current phrase for user: {current_phrase}")

    if not current_phrase:
        await query.message.answer("No active phrase to show examples for!")
        return

    data = read_user_data()

    # Filter the data to only include rows that match the current phrase
    matching_data = [row for row in data if row["current_phrase"] == current_phrase]

    print(f"[DEBUG] Number of matching examples for current phrase: {len(matching_data)}")

    if not matching_data:
        keyboard = [
        [
            InlineKeyboardButton(text="Назад", callback_data=f"back_to_main:{current_phrase}"),
        ],
    ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await query.message.edit_text(f"Чёт никто ничего не придумал на {current_phrase}!", reply_markup=reply_markup)
        return

    # Choose a random example and display it
    new_example = random.choice(matching_data)
    example_text = new_example["user_message"]
    print(f"[DEBUG] Chosen example for display: {example_text}")

    # Define the reply_markup variable with the keyboard
    keyboard = [
        [
            InlineKeyboardButton(text="Ещё", callback_data="show_example"),
            InlineKeyboardButton(text="Назад", callback_data=f"back_to_main:{current_phrase}"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await query.message.edit_text(f"{example_text}", reply_markup=reply_markup)

async def handle_back_to_main(query, user_id):
    print("[DEBUG] Entered handle_back_to_main function.")
    current_phrase = query.data.split(":", 1)[1]
    
    # Adjusting the keyboard to include the "Additional Challenge" button.
    keyboard = [
        [
            InlineKeyboardButton(text="Change Phrase", callback_data="change_phrase"),
            InlineKeyboardButton(text="Show Example", callback_data=f"show_example"),
        ],
        [
            InlineKeyboardButton(text="Additional Challenge", callback_data="add_challenge"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    try:
        await query.message.edit_text(f"<b>{current_phrase}</b>", parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e:
        print(f"[DEBUG] Error occurred while editing the message: {e}")

async def handle_battle(query, user_id):
    await query.message.answer("Rhyme as much as you can in 3 minutes", reply_markup=get_battle_start_keyboard())

async def handle_start_battle(query, user_id):
    await handle_play(query, user_id)
    battle_id = str(uuid.uuid4())  # Generate a unique ID for this battle
    battles[battle_id] = {
        "start_time": asyncio.get_event_loop().time(),
        "participants": {
            user_id: {
                "score": 0,
                "responses": []
            }
        }
    }
    await asyncio.sleep(60)  # 1 minute
    await end_battle(query, battle_id)

async def handle_battle_again(query, user_id):
    await handle_battle(query, user_id)

async def handle_back_to_menu(query, user_id):
    await query.message.answer("Welcome back to the main menu!", reply_markup=get_start_keyboard())

async def end_battle(query, battle_id):
    battle_data = battles.get(battle_id)
    if not battle_data:
        await query.message.answer("Error ending battle!")
        return

    scores = [(data["full_name"], data["score"]) for user, data in battle_data["participants"].items()]
    scores.sort(key=lambda x: x[1], reverse=True)

    leaderboard = "Результаты Баттла:\n"
    for i, (full_name, score) in enumerate(scores, 1):
        leaderboard += f"{i}. {full_name}: {score}\n"
    
    await query.message.answer(leaderboard, reply_markup=get_battle_end_keyboard())
