from user_data import read_user_data
import random
import csv
import os
from constants import battles

# Determine the base directory and the paths to the files in the /data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHRASES_PATH = os.path.join(BASE_DIR, "data", "phrases.txt")
CHALLENGES_PATH = os.path.join(BASE_DIR, "data", "challenges.txt")

def get_random_phrase():
    phrases = read_phrases_from_file()
    phrase = random.choice(phrases).strip()
    return f"<b>{phrase}</b>"

def in_battle(user_id):
    for battle_data in battles.values():
        if user_id in battle_data["participants"]:
            return True
    return False


def get_random_challenge():
    with open(CHALLENGES_PATH, "r", encoding="utf-8") as file:
        challenges = file.readlines()
    challenge = random.choice(challenges).strip()
    number, text = challenge.split('. ', 1)  # Splitting by the first period to get the number
    return int(number), f"<i>{text}</i>"

def read_phrases_from_file():
    with open(PHRASES_PATH, "r", encoding="utf-8") as file:
        return file.readlines()

def check_message_length(message_text: str, current_phrase: str) -> bool:
    return len(message_text) != len(current_phrase)

def jaccard_similarity(set1: set, set2: set) -> float:
    intersection_size = len(set1.intersection(set2))
    union_size = len(set1.union(set2))
    return intersection_size / union_size

def start_battle():
    with open(PHRASES_PATH, 'r', encoding='utf-8') as file:
        phrases = file.readlines()
    return random.choice(phrases).strip()


def is_valid_response(user_message: str, current_phrase: str, challenge: bool = False) -> bool:
    print(f"[DEBUG] Checking validation for response '{user_message}' against challenge '{current_phrase}'")
    
    # If it's a challenge, we only check if the user message is not empty
    if challenge:
        result = bool(user_message.strip())
        print(f"[DEBUG] Challenge validation result: {result}")
        return result

    if user_message.lower() == current_phrase.lower():
        print("[DEBUG] User's response matched exactly with the challenge.")
        return False

    if len(user_message) < len(current_phrase):
        print("[DEBUG] User's response is shorter than the challenge.")
        return False

    phrase_chars = set(current_phrase)
    if not phrase_chars:
        print("[DEBUG] The challenge has no distinct characters.")
        return False

    matching_chars = sum(1 for char in phrase_chars if char in user_message)
    matching_percentage = (matching_chars / len(phrase_chars)) * 100

    print(f"[DEBUG] Matching character percentage: {matching_percentage}%")
    
    is_valid = matching_percentage >= 50
    print(f"[DEBUG] Validation result: {is_valid}")
    return is_valid

def get_word_frequencies() -> dict:
    data = read_user_data()
    word_frequencies = {}

    for row in data:
        current_phrase = row["current_phrase"]
        if current_phrase not in word_frequencies:
            word_frequencies[current_phrase] = 0
        word_frequencies[current_phrase] += 1

    return word_frequencies