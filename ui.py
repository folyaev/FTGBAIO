from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_change_phrase_keyboard():
    change_btn = InlineKeyboardButton(text="Change Phrase", callback_data="change_phrase")
    example_btn = InlineKeyboardButton(text="Show Example", callback_data="show_example")
    challenge_btn = InlineKeyboardButton(text="Additional Challenge", callback_data="add_challenge")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [change_btn, example_btn],
        [challenge_btn]
    ])
    return keyboard   

def get_battle_start_keyboard():
    start_btn = InlineKeyboardButton(text="Start Battle", callback_data="start_battle")
    return InlineKeyboardMarkup(inline_keyboard=[[start_btn]])

def get_battle_end_keyboard():
    again_btn = InlineKeyboardButton(text="Battle Again", callback_data="battle_again")
    menu_btn = InlineKeyboardButton(text="Back to Menu", callback_data="back_to_menu")
    return InlineKeyboardMarkup(inline_keyboard=[[again_btn, menu_btn]])

# Update the get_start_keyboard function to include the 'Battle' button:
def get_start_keyboard():
    play_btn = InlineKeyboardButton(text="Play", callback_data="play")
    battle_btn = InlineKeyboardButton(text="Battle", callback_data="battle")  # New Battle button
    help_btn = InlineKeyboardButton(text="Help", callback_data="help")
    leaderboard_btn = InlineKeyboardButton(text="Leaderboard", callback_data="leaderboard")

    return InlineKeyboardMarkup(inline_keyboard=[
        [play_btn, battle_btn],  # Add the new Battle button here
        [help_btn],
        [leaderboard_btn]
    ])
