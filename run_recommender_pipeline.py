
"""
run_recommender_pipeline.py

Runner file that connects the TWO files we already made:

1) smart_profile_recommender_v2.py
   - User Profile questions
   - Profile-based recommendations
   - BM25/profile scoring helpers

2) semantic_hybrid_recommender.py
   - Embeddings
   - Semantic similarity
   - Hybrid search: BM25 + Embeddings + Profile

Put this file in the same folder with:
- processed.json
- smart_profile_recommender_v2.py
- semantic_hybrid_recommender.py

Install once:
    pip install sentence-transformers numpy

Run:
    python run_recommender_pipeline.py
"""

from smart_profile_recommender_v2 import (
    UserProfile,
    DatasetOptionsBuilder,
    SmartProfileRecommender,
    PROJECT_TYPE_OPTIONS,
    GOAL_OPTIONS,
    LEVEL_OPTIONS,
    REPO_KIND_OPTIONS,
    COMPLEXITY_OPTIONS,
    choose_one,
    print_results,
)

from semantic_hybrid_recommender import SemanticHybridRecommender


def main():
    data_path = "processed.json"

    # ============================================================
    # 1) Build website/profile options from existing dataset
    # ============================================================
    options_builder = DatasetOptionsBuilder(data_path)
    website_options = options_builder.save_website_options("smart_profile_options.json")

    print("\n====================================================")
    print("Unified Runner: Profile Recommender + Semantic Hybrid Search")
    print("====================================================\n")

    print("This file only RUNS the two existing files:")
    print("- smart_profile_recommender_v2.py")
    print("- semantic_hybrid_recommender.py\n")

    # ============================================================
    # 2) Ask User Profile questions ONCE
    # ============================================================
    project_type = choose_one(
        "Q1) What type of project are you looking for?",
        website_options["project_types"],
        True
    )

    language = choose_one(
        "Q2) Which programming language do you prefer?",
        website_options["languages"],
        True
    )

    goal = choose_one(
        "Q3) What is your goal?",
        website_options["goals"],
        True
    )

    level = choose_one(
        "Q4) What is your skill level?",
        website_options["levels"],
        True
    )

    repo_kind = choose_one(
        "Q5) What kind of repository do you prefer?",
        website_options["repo_kinds"],
        True
    )

    complexity = choose_one(
        "Q6) How complex should the project be?",
        website_options["complexities"],
        True
    )

    profile = UserProfile(
        project_type=project_type,
        language=language,
        goal=goal,
        level=level,
        repo_kind=repo_kind,
        complexity=complexity,
        top_k=5
    )

    print("\n====================================================")
    print("Your selected profile")
    print("====================================================")
    print(f"project_type: {profile.project_type}")
    print(f"language: {profile.language}")
    print(f"goal: {profile.goal}")
    print(f"level: {profile.level}")
    print(f"repo_kind: {profile.repo_kind}")
    print(f"complexity: {profile.complexity}")

    # ============================================================
    # 3) Before query: profile-based recommendation
    #    This uses smart_profile_recommender_v2.py
    # ============================================================
    print("\n[STEP 1] Running profile-based recommender...")
    profile_recommender = SmartProfileRecommender(data_path)

    profile_results = profile_recommender.recommend_for_profile(profile)

    print_results(
        "Recommended for you based on your profile",
        profile_results
    )

    # ============================================================
    # 4) After query: semantic hybrid search
    #    This uses semantic_hybrid_recommender.py
    # ============================================================
    query = input("\nNow type your search query, or press Enter to skip: ").strip()

    if not query:
        print("\nSearch skipped.")
        return

    print("\n[STEP 2] Running semantic hybrid search...")
    print("This combines BM25 + embeddings + profile matching.\n")

    semantic_recommender = SemanticHybridRecommender(data_path)

    hybrid_results = semantic_recommender.search_with_profile_and_semantics(
        query=query,
        profile=profile,
        top_k=10
    )

    print_results(
        f"Hybrid semantic search results for query: {query}",
        hybrid_results
    )


if __name__ == "__main__":
    main()
