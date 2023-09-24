from enum import Enum

last_entries = {}
battles = {}  # This will store ongoing battles

class Command(Enum):
    PLAY = "play"
    CHANGE_PHRASE = "change_phrase"
    HELP = "help"
    LEADERBOARD = "leaderboard"
    SHOW_EXAMPLE = "show_example"
    ADD_CHALLENGE = "add_challenge"
    BACK_TO_MAIN = "back_to_main"
    BATTLE = "battle"
    START_BATTLE = 'start_battle'