import json
import math
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DISHES_FILE = os.path.join(BASE_DIR, "dishes.json")
USERS_FILE = os.path.join(BASE_DIR, "user_data.json")
FEATURE_KEYS = ["spice", "sweetness", "texture", "heaviness"]

# ── Vector math ──

def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def _magnitude(v):
    return math.sqrt(sum(x * x for x in v))

def cosine_similarity(vec_a, vec_b):
    dot = _dot(vec_a, vec_b)
    mag_a = _magnitude(vec_a)
    mag_b = _magnitude(vec_b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

def dish_vector(dish):
    return [dish[k] for k in FEATURE_KEYS]

# ── Data I/O ──

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
    raise ValueError(f"User '{username}' not found.")

def update_allergies(username, allergies):
    data = load_users()
    for user in data["users"]:
        if user["username"].lower() == username.lower():
            user["allergies"] = allergies
            save_users(data)
            return

# ── Recommendation pipeline ───

def get_recommendations(user_vector, province, allergies, username):
    dishes = load_dishes()
    user, _ = get_or_create_user(username)
    disliked = set(user["disliked_ids"])
    allergy_set = set(a.lower() for a in allergies)

    # Province filter
    pool = [d for d in dishes if d["province"].lower() == province.lower()]

    # Allergen hard-block
    pool = [
        d for d in pool
        if not allergy_set.intersection(set(a.lower() for a in d.get("allergens", [])))
    ]

    # Disliked hard-block
    pool = [d for d in pool if d["id"] not in disliked]

    # Cosine-similarity ranking
    scored = [(cosine_similarity(user_vector, dish_vector(d)), d) for d in pool]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [dish for _, dish in scored[:5]]

# ── CLI Interface ───

def input_vector():
    print("Enter your preferences (0-10) for each feature:")
    return [float(input(f"{f}: ")) for f in FEATURE_KEYS]

def main():
    print("=== Dish Recommendation CLI ===")
    username = input("Enter your username: ").strip()
    user, _ = get_or_create_user(username)

    while True:
        print("\nOptions:")
        print("1. Update allergies")
        print("2. Get recommendations")
        print("3. Dislike a dish")
        print("4. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            allergies = input("Enter your allergies (comma-separated): ").split(",")
            allergies = [a.strip() for a in allergies if a.strip()]
            update_allergies(username, allergies)
            print("Allergies updated.")

        elif choice == "2":
            province = input("Enter province: ").strip()
            user_vector = input_vector()
            recommendations = get_recommendations(user_vector, province, user.get("allergies", []), username)
            if recommendations:
                print("\nTop recommendations:")
                for d in recommendations:
                    print(f"- {d['name']} (ID: {d['id']})")
            else:
                print("No dishes match your preferences.")

        elif choice == "3":
            dish_id = input("Enter Dish ID to dislike: ").strip()
            add_dislike(username, dish_id)
            print("Dish added to your disliked list.")

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    main()