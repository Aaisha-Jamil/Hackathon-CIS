🍽️ PalatePal

Overview

PalatePal is a content-based dish recommendation system that personalizes food suggestions based on individual taste preferences. Instead of recommending popular or trending dishes, the system models user taste numerically and ranks dishes based on similarity.
Each user is represented through a 4-dimensional taste profile consisting of spice, sweetness, texture, and heaviness. Dishes are encoded using the same structure, allowing direct mathematical comparison.
The system also respects real-world constraints such as allergies and previously disliked dishes. By combining rule-based filtering with vector similarity ranking, PalatePal delivers personalized and safe recommendations.



Program Flow

The program begins by loading the dish dataset and retrieving (or creating) a user profile. Each user has persistent data including disliked dishes and allergies, stored in JSON format.
When recommendations are requested, the system first applies deterministic filters. It narrows the dish pool by province, removes dishes containing allergens, and excludes any dishes the user has previously disliked.
After filtering, both the user profile and remaining dishes are represented as 4-dimensional vectors. The system computes cosine similarity between the user vector and each dish vector to measure alignment in taste space.
The dishes are then sorted in descending order of similarity score. Finally, the top five highest-ranked dishes are returned as personalized recommendations.



Tech Stack

Python
JSON (dataset and user persistence)
Manual implementation of cosine similarity
Content-based filtering architecture
