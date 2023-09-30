from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from game_logic import get_random_phrase, get_random_challenge, start_battle
from ui import get_change_phrase_keyboard, get_battle_start_keyboard, get_battle_end_keyboard, get_start_keyboard
from utils.utilities import clean_html_tags
from user_data import read_user_data
from constants import last_entries, battles, current_phrases
import asyncio  # New import
import uuid
import logging

import random

logger = logging.getLogger(__name__)

async def handle_play(query, user_id):
    chat_id = query.message.chat.id
    phrase = get_random_phrase()
    current_phrases[chat_id] = (phrase, False)
    keyboard = get_change_phrase_keyboard()

    # Capture the message_id of the sent message
    sent_message = await query.message.answer(phrase, reply_markup=keyboard, parse_mode='HTML')
    battles[chat_id]['current_phrase_message_id'] = sent_message.message_id

async def handle_change_phrase(query, user_id):
    chat_id = query.message.chat.id
    new_phrase = get_random_phrase()
    current_phrases[chat_id] = (new_phrase, False)
    keyboard = get_change_phrase_keyboard()
    await query.message.edit_text(new_phrase, reply_markup=keyboard, parse_mode='HTML')

async def handle_add_challenge(query, user_id):
    chat_id = query.message.chat.id
    challenge_number, challenge_text = get_random_challenge()
    
    # Store the challenge in current_phrases with is_challenge set to True
    current_phrases[chat_id] = ((challenge_number, challenge_text), True)
    
    sent_message = await query.message.answer(challenge_text, parse_mode='HTML')
    
    # Update the battles dictionary for the given chat_id
    if chat_id not in battles:
        battles[chat_id] = {}
    
    # Update the challenge_message_id, keeping existing data intact
    battles[chat_id]["challenge_message_id"] = sent_message.message_id
    
    # Debugging log to track the state of the 'battles' dictionary
    print(f"[DEBUG] Updated battles after adding challenge: {battles}")



async def handle_show_example(query, user_id):
    print("[DEBUG] Entered handle_show_example function.")

    chat_id = query.message.chat.id  # Get chat_id from the query message
    
    # Check current_phrases instead of last_entries
    if chat_id not in current_phrases:  
        print("[DEBUG] Chat does not have an active phrase.")
        await query.message.answer("No active phrase to show examples for!")
        return

    current_phrase_data = current_phrases.get(chat_id)
    current_phrase = clean_html_tags(current_phrase_data[0]) if not current_phrase_data[1] else None
    print(f"[DEBUG] Cleaned current phrase for chat: {current_phrase}")

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
        await query.message.edit_text(f"Чёт никто ничего не придумал на <b>{current_phrase}</b>!", parse_mode="HTML", reply_markup=reply_markup)
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
            InlineKeyboardButton(text="Show Example", callback_data=f"show_example:{current_phrase}"),
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
    chat_id = query.message.chat.id
    battle_id = chat_id  # Use chat_id as the battle identifier

    if battle_id not in battles or "participants" not in battles[battle_id]:
        battles[battle_id] = {
            "start_time": asyncio.get_event_loop().time(),
            "participants": {}
        }

    # Add the user to the participants with their full name and initialize their score and responses
    battles[battle_id]["participants"][user_id] = {
        "full_name": query.from_user.full_name,
        "score": 0,
        "responses": []
    }

    await asyncio.sleep(20)  # 20 seconds
    await end_battle(query, battle_id)

async def handle_battle_again(query, user_id):
    await handle_battle(query, user_id)

async def handle_back_to_menu(query, user_id):
    await query.message.answer("Welcome back to the main menu!", reply_markup=get_start_keyboard())

async def end_battle(query, battle_id):
    print(f"[DEBUG] Ending battle for battle_id: {battle_id}")  # Debug line 1
    print(f"[DEBUG] Current battles state: {battles}")  # Debug line 2

    battle_data = battles.get(battle_id)
    if not battle_data:
        await query.message.answer("Error ending battle!")
        return

    if "participants" in battle_data:
        scores = [(data.get("full_name", "Unknown User"), data["score"]) for user, data in battle_data["participants"].items()]
        scores.sort(key=lambda x: x[1], reverse=True)
    else:
        await query.message.answer("No participants found!")
        return

    leaderboard = "Результаты Баттла:\n"
    for i, (full_name, score) in enumerate(scores, 1):
        leaderboard += f"{i}. {full_name}: {score}\n"

    chat_id = query.message.chat.id
    if chat_id in current_phrases:
        del current_phrases[chat_id]

    await query.message.answer(leaderboard, reply_markup=get_battle_end_keyboard())


