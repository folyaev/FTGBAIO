import csv
import os

# Determine the base directory and the path to the user_data.csv in the /data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "user_data.csv")

phrase_hash_to_phrase = {}

def save_entry(username: str, current_phrase: str, user_message: str, score: int, challenge_number: int = 0) -> None:
    with open(DATA_PATH, mode="a", newline="", encoding="utf-8") as file:
        fieldnames = ["username", "current_phrase", "user_message", "score", "challenge_number"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({
            "username": username,
            "current_phrase": current_phrase,
            "user_message": user_message,
            "score": score,
            "challenge_number": challenge_number
        })

def read_user_data() -> list:
    data = []

    with open(DATA_PATH, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 5:  # Updated this condition
                username, current_phrase, user_message, score, challenge_number = row
                data.append({"username": username, "current_phrase": current_phrase, "user_message": user_message, "score": score, "challenge_number": challenge_number})

    return data
