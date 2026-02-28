"""
PalatePal — Pakistan Food Explorer

A CLI-based recommendation system that filters a 100-dish database
based on province, allergies, and taste preferences.
"""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DISHES_FILE = os.path.join(BASE_DIR, "dishes.json")
USERS_FILE = os.path.join(BASE_DIR, "user_data.json")

PROVINCES = ["Punjab", "Sindh", "KPK", "Baluchistan"]
ALLERGY_OPTIONS = ["dairy", "nuts", "gluten", "eggs"]


# -------------------- Data Handling --------------------

def load_dishes():
    with open(DISHES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_users():
    if not os.path.exists(USERS_FILE):
        return {"users": []}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_or_create_user(username):
    data = load_users()
    for user in data["users"]:
        if user["username"].lower() == username.lower():
            return user, data

    new_user = {"username": username, "disliked_ids": [], "allergies": []}
    data["users"].append(new_user)
    save_users(data)
    return new_user, data


def add_dislike(username, dish_id):
    data = load_users()
    for user in data["users"]:
        if user["username"].lower() == username.lower():
            if dish_id not in user["disliked_ids"]:
                user["disliked_ids"].append(dish_id)
            save_users(data)
            return
    raise ValueError("User not found.")


def update_allergies(username, allergies):
    data = load_users()
    for user in data["users"]:
        if user["username"].lower() == username.lower():
            user["allergies"] = allergies
            save_users(data)
            return


# -------------------- Scoring Logic --------------------

def _score_savory(dish, answers):
    score = 0

    heat_diff = abs(dish["spice_level"] - answers["heat"])
    score += max(0, 5 - heat_diff)

    if answers["texture"] == dish["texture"]:
        score += 5

    if answers["profile"] == dish.get("profile"):
        score += 5

    if answers["adventurous"]:
        if dish.get("contains_organ_meat"):
            score += 3
    else:
        if dish.get("contains_organ_meat"):
            score -= 100

    return score


def _score_sweet(dish, answers):
    score = 0

    if answers["temp"] == dish.get("serving_temp"):
        score += 5

    if answers["consistency"] == dish.get("texture"):
        score += 5

    if answers["nut_preference"] == dish.get("nut_level"):
        score += 5

    if answers["intensity"] == dish.get("sweetness_intensity"):
        score += 5

    return score


# -------------------- Recommendation Engine --------------------

def get_recommendations(user_profile):
    dishes = load_dishes()
    user, _ = get_or_create_user(user_profile["username"])

    disliked = set(user["disliked_ids"])
    allergies = set(a.lower() for a in user_profile["allergies"])

    pool = dishes

    pool = [d for d in pool if d["province"] == user_profile["province"]]

    pool = [
        d for d in pool
        if not allergies.intersection(set(a.lower() for a in d.get("allergens", [])))
    ]

    pool = [d for d in pool if d["id"] not in disliked]

    pool = [d for d in pool if d["taste_type"] == user_profile["taste_type"]]

    scored = []
    for dish in pool:
        if user_profile["taste_type"] == "Savory":
            s = _score_savory(dish, user_profile["quiz_answers"])
        else:
            s = _score_sweet(dish, user_profile["quiz_answers"])
        scored.append((s, dish))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [dish for _, dish in scored[:5]]


# -------------------- CLI --------------------

def ask_username():
    name = input("\nEnter your username: ").strip()
    while not name:
        name = input("Username cannot be empty. Try again: ").strip()
    return name


def ask_allergies():
    print("\nAllergy check")
    for i, a in enumerate(ALLERGY_OPTIONS, 1):
        print(f"[{i}] {a}")

    raw = input("Enter numbers separated by commas, or press Enter for none: ").strip()
    if not raw:
        return []

    chosen = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit() and 1 <= int(part) <= len(ALLERGY_OPTIONS):
            chosen.append(ALLERGY_OPTIONS[int(part) - 1])
    return chosen


def ask_province():
    print("\nSelect a province")
    for i, p in enumerate(PROVINCES, 1):
        print(f"[{i}] {p}")

    while True:
        raw = input("Your choice (1-4): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 4:
            return PROVINCES[int(raw) - 1]
        print("Invalid choice. Try again.")


def ask_taste_type():
    print("\nWhat are you in the mood for?")
    print("[1] Savory")
    print("[2] Sweet")

    while True:
        raw = input("Your choice: ").strip()
        if raw == "1":
            return "Savory"
        if raw == "2":
            return "Sweet"
        print("Invalid choice.")


def display_results(results):
    if not results:
        print("\nNo dishes match your preferences.")
        return

    print("\nTop Recommendations")
    for i, dish in enumerate(results, 1):
        print(f"\n{i}. {dish['name']}")
        print(f"Province: {dish['province']} | Type: {dish['veg_nonveg']}")
        print(f"Spice Level: {dish['spice_level']}")
        print(f"Description: {dish['description']}")


def feedback_loop(results, username):
    if not results:
        return

    print("\nRate each dish: L = Like, D = Dislike, S = Skip")

    for dish in results:
        while True:
            raw = input(f"{dish['name']} (L/D/S): ").strip().upper()
            if raw == "L":
                break
            elif raw == "D":
                add_dislike(username, dish["id"])
                break
            elif raw == "S":
                break
            else:
                print("Enter L, D, or S.")
def ask_savory_quiz():
    answers = {}

    while True:
        raw = input("Preferred spice level (1-5): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 5:
            answers["heat"] = int(raw)
            break
        print("Enter a number between 1 and 5.")

    print("Texture preference:")
    print("[1] Dry/Roasted")
    print("[2] Gravy/Stew")
    while True:
        raw = input("Choice: ").strip()
        if raw == "1":
            answers["texture"] = "Dry/Roasted"
            break
        if raw == "2":
            answers["texture"] = "Gravy/Stew"
            break
        print("Invalid choice.")

    print("Flavor profile:")
    print("[1] Aromatic")
    print("[2] Tangy")
    while True:
        raw = input("Choice: ").strip()
        if raw == "1":
            answers["profile"] = "Aromatic"
            break
        if raw == "2":
            answers["profile"] = "Tangy"
            break
        print("Invalid choice.")

    while True:
        raw = input("Include organ meats? (Y/N): ").strip().upper()
        if raw in ("Y", "N"):
            answers["adventurous"] = raw == "Y"
            break
        print("Enter Y or N.")

    return answers


def ask_sweet_quiz():
    answers = {}

    print("Preferred temperature:")
    print("[1] Warm")
    print("[2] Cold")
    while True:
        raw = input("Choice: ").strip()
        if raw == "1":
            answers["temp"] = "Warm"
            break
        if raw == "2":
            answers["temp"] = "Cold"
            break
        print("Invalid choice.")

    print("Consistency preference:")
    print("[1] Liquid/Creamy")
    print("[2] Solid/Dense")
    while True:
        raw = input("Choice: ").strip()
        if raw == "1":
            answers["consistency"] = "Liquid/Creamy"
            break
        if raw == "2":
            answers["consistency"] = "Solid/Dense"
            break
        print("Invalid choice.")

    print("Nut preference:")
    print("[1] Nut-heavy")
    print("[2] Plain")
    while True:
        raw = input("Choice: ").strip()
        if raw == "1":
            answers["nut_preference"] = "Nut-heavy"
            break
        if raw == "2":
            answers["nut_preference"] = "Plain"
            break
        print("Invalid choice.")

    print("Sweetness intensity:")
    print("[1] Mild")
    print("[2] Syrupy")
    while True:
        raw = input("Choice: ").strip()
        if raw == "1":
            answers["intensity"] = "Mild"
            break
        if raw == "2":
            answers["intensity"] = "Syrupy"
            break
        print("Invalid choice.")

    return answers

def main():
    print("\nPalatePal - Pakistan Food Explorer")

    username = ask_username()
    user, _ = get_or_create_user(username)

    allergies = ask_allergies()
    update_allergies(username, allergies)

    province = ask_province()
    taste_type = ask_taste_type()

    if taste_type == "Savory":
        quiz_answers = ask_savory_quiz()
    else:
        quiz_answers = ask_sweet_quiz()

    profile = {
        "username": username,
        "allergies": allergies,
        "province": province,
        "taste_type": taste_type,
        "quiz_answers": quiz_answers,
    }

    results = get_recommendations(profile)
    display_results(results)
    feedback_loop(results, username)

    print("\nThank you for using PalatePal.\n")


if __name__ == "__main__":
    main()