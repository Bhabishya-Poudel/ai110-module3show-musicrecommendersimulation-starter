"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, match_label, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Taste profile: an upbeat, mostly electronic pop listener
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "valence": 0.82,
        "acousticness": 0.20,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations")
    print("=" * 52)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']}")
        print(f"   Overall: {match_label(score)}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


if __name__ == "__main__":
    main()
