PalatePal – AI-Powered Dish Recommender


1.  Problem Understanding

Choosing what to eat is a daily decision problem. Most food platforms
show popular or sponsored items — not dishes aligned with a user’s
actual taste profile, dietary restrictions, and dislikes.

The goal of PalatePal is to build a personalized dish recommendation
system that:

-   Learns user taste preferences (spice, sweetness, texture, heaviness)
-   Respects allergies and dietary restrictions
-   Avoids previously disliked dishes
-   Returns relevant, explainable recommendations
-   Continuously improves through user feedback

This project goes beyond static filtering — it evolves into a true
AI-based recommendation engine.


2.  Approach

Phase 1 – Hardcoded Filtering (Initial Prototype)

The project initially started with rule-based filtering:

-   Filter dishes by province
-   Remove dishes containing allergens
-   Remove previously disliked dishes
-   Manually rank dishes based on simple preference matching

While functional, this approach was rigid and did not scale well. It
lacked intelligent ranking and personalization depth.

Phase 2 – AI-Based Model Training (Final Implementation)

Content-Based Filtering using Cosine Similarity

Each dish is represented as a 4-dimensional feature vector: [spice,
sweetness, texture, heaviness]

User preferences are also converted into a 4-D vector.

The system computes cosine similarity between: - User preference
vector - Dish feature vector

Dishes are ranked by similarity score, and the top 5 are returned.

This allows: - Personalized ranking instead of static filtering - Better
alignment with nuanced taste profiles - Scalable and mathematically
grounded recommendation logic

Final Recommendation Pipeline

1.  Province Filter
2.  Allergen Hard Block
3.  Disliked Dish Hard Block
4.  Cosine Similarity Ranking
5.  Top 5 Results Returned

This hybrid system combines: - Deterministic filtering (safety
constraints) - Machine learning–based ranking (intelligence layer)


3.  What I Implemented

Backend (Core Logic) – Implemented by Me

Built with AI guidance, but fully understood and structured by me.

I implemented: - Vector math functions (dot product, magnitude, cosine
similarity) - Dish vector extraction logic - User data persistence using
JSON - Disliked dish memory system - Allergy overwrite and management -
Recommendation ranking engine - Top-5 intelligent selection logic -
Clean modular architecture

All backend filtering, ranking, and data flow is my implementation.

Frontend – Pure Vibe Coding

The frontend was built creatively and rapidly to: - Capture onboarding
quiz inputs - Allow user rating (Liked / Disliked) - Update user
profile - Display recommendations cleanly

The focus of this project is the AI backend, while the frontend
prioritizes usability and presentation.


4.  Dataset

-   80–100 structured dishes
-   Multiple cuisines
-   Province tagging
-   Allergen tagging
-   4-feature numerical taste encoding
-   Original structured JSON dataset

Each dish contains: - ID - Cuisine - Province - Taste attributes (1–5
scale) - Allergen tags - Description

This structure enables vector-based ML ranking.


5.  Challenges Faced

-Learning Machine Learning from Scratch

Machine learning was completely new to me.

Challenges included: - Understanding vector space representation -
Implementing cosine similarity mathematically - Learning how
content-based filtering works - Translating taste into numerical
dimensions

This was the biggest learning curve of the project.

-Designing a Meaningful Feature Space

Converting “taste” into measurable attributes required: - Selecting
relevant dimensions - Normalizing them into consistent scales - Ensuring
fair similarity scoring

Balancing interpretability and effectiveness was difficult.

-Feedback Loop Design

Ensuring disliked dishes never reappear required: - Persistent storage -
Efficient lookup - Clean user-state management


6.  Technical Highlights

-   AI-driven ranking using cosine similarity
-   Hybrid deterministic + ML filtering pipeline
-   Persistent user state (JSON-based storage)
-   Dynamic profile updating
-   Scalable architecture
-   Clean modular Python backend


7.  Why This Is an AI Project

This system: - Represents user preferences as feature vectors - Uses
mathematical similarity modeling - Performs intelligent ranking - Adapts
through user feedback

It is not a static filter — it is a content-based recommender system
grounded in vector space modeling.


8.  Future Improvements

-   Collaborative filtering (multi-user similarity)
-   Real ML model training using scikit-learn
-   Natural language preference input
-   Restaurant API integration
-   Weather-based suggestions
-   Nutritional optimization layer


9.  Conclusion

PalatePal evolved from a rule-based filter into a true AI-powered
recommendation engine.
This project represents: - My transition from hardcoded logic to machine
learning concepts - My first hands-on implementation of content-based
filtering - A complete backend system built and understood by me - A
fully functional live-demo–ready application
It is not just a recommender — it is proof of growth into AI system
design.
