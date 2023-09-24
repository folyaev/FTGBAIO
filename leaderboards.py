import csv
from collections import defaultdict
from constants import battles
import os
from user_data import read_user_data

# Determine the base directory and the path to the user_data.csv in the /data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "user_data.csv")

def get_total_score(username: str) -> int:
    total_score = 0
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                total_score += int(row["score"])
    return total_score

def get_leaderboard():
    user_scores = defaultdict(int)  # Use a default dictionary to accumulate scores
    user_data = read_user_data()

    for entry in user_data:
        username = entry["username"]
        score = int(entry["score"])  # Convert the score to an integer
        user_scores[username] += score  # Accumulate the score

    # Sort by score in descending order and return as a list of tuples
    sorted_leaderboard = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_leaderboard


    return sorted_leaderboard

def generate_leaderboard():
    leaderboard = get_leaderboard()
    leaderboard_message = "🏆 Leaderboard 🏆\n\n"

    for idx, (username, score) in enumerate(leaderboard, 1):
        leaderboard_message += f"{idx}. {username}: {score} points\n"

    return leaderboard_message

def display_battle_leaderboard(battle_id: str):
    battle_data = battles[battle_id]
    print(battle_data)
    
    sorted_participants = sorted(battle_data["participants"].items(), key=lambda x: x[1]["score"], reverse=True)
    
    leaderboard_text = "Результаты баттла:\n"
    for idx, (user_id, user_data) in enumerate(sorted_participants):
        leaderboard_text += f"{idx + 1}. {user_data['full_name']} - {user_data['score']} points\n"
    
    return leaderboard_text