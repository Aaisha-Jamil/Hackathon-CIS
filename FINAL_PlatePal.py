"""
PalatePal Recommender Engine
───────────────────────────
Content-Based Filtering using Cosine Similarity on 4-D feature vectors.
Feature dimensions: spice, sweetness, texture, heaviness  (each 1-5).

Filtering pipeline
  1. Province filter
  2. Allergen hard-block
  3. Disliked-ID hard-block
  4. Cosine-similarity ranking → Top 5
"""

import json
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DISHES_FILE = os.path.join(BASE_DIR, "dishes.json")
USERS_FILE = os.path.join(BASE_DIR, "user_data.json")

FEATURE_KEYS = ["spice", "sweetness", "texture", "heaviness"]


# ── Vector math ─────────────────────────────────────────────────────────────

def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _magnitude(v):
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(vec_a, vec_b):
    """Return cosine similarity between two equal-length numeric vectors."""
    dot = _dot(vec_a, vec_b)
    mag_a = _magnitude(vec_a)
    mag_b = _magnitude(vec_b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def dish_vector(dish):
    """Extract the 4-D feature vector from a dish dict."""
    return [dish[k] for k in FEATURE_KEYS]


# ── Data I/O ────────────────────────────────────────────────────────────────

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
    """Return (user_dict, full_data) for an existing or brand-new user."""
    data = load_users()
    for user in data["users"]:
        if user["username"].lower() == username.lower():
            return user, data
    new_user = {"username": username, "disliked_ids": [], "allergies": []}
    data["users"].append(new_user)
    save_users(data)
    return new_user, data


def add_dislike(username, dish_id):
    """Append a dish ID to a user's disliked list (unique)."""
    data = load_users()
    for user in data["users"]:
        if user["username"].lower() == username.lower():
            if dish_id not in user["disliked_ids"]:
                user["disliked_ids"].append(dish_id)
            save_users(data)
            return
    raise ValueError(f"User '{username}' not found.")


def update_allergies(username, allergies):
    """Overwrite a user's allergy list."""
    data = load_users()
    for user in data["users"]:
        if user["username"].lower() == username.lower():
            user["allergies"] = allergies
            save_users(data)
            return


# ── Recommendation pipeline ────────────────────────────────────────────────

def get_recommendations(user_vector, province, allergies, username):
    """
    Parameters
    ----------
    user_vector : list[int|float]   4-D preference vector [spice, sweetness, texture, heaviness]
    province    : str               e.g. "Punjab"
    allergies   : list[str]         e.g. ["dairy", "nuts"]
    username    : str               for dislike look-up

    Returns
    -------
    list[dict] – top-5 dishes sorted by cosine similarity (descending).
    """
    dishes = load_dishes()
    user, _ = get_or_create_user(username)
    disliked = set(user["disliked_ids"])
    allergy_set = set(a.lower() for a in allergies)

    # 1. Province filter
    pool = [d for d in dishes if d["province"] == province]

    # 2. Allergen hard-block
    pool = [
        d for d in pool
        if not allergy_set.intersection(set(a.lower() for a in d.get("allergens", [])))
    ]

    # 3. Disliked hard-block
    pool = [d for d in pool if d["id"] not in disliked]

    # 4. Cosine-similarity ranking
    scored = []
    for d in pool:
        sim = cosine_similarity(user_vector, dish_vector(d))
        scored.append((sim, d))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [dish for _, dish in scored[:5]]
