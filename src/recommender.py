import csv
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

WEIGHTS = {"energy": 0.35, "valence": 0.25, "mood": 0.20, "acousticness": 0.10, "genre": 0.10}
MIN_SCORE = 0.5      # songs scoring below this are not a real match
MIN_MATCHES = 1       # if fewer songs than this clear MIN_SCORE, fall back to closest ones
EXPLORE_CHANCE = 0.1 # chance per call that one slot becomes a random surprise pick

# (minimum value, label), best first. Used for both per-feature closeness and the final score.
MATCH_LABELS = [
    (0.95, "closest match"),
    (0.85, "closer match"),
    (0.70, "close match"),
    (0.50, "near match"),
    (0.00, "distant match"),
]

def match_label(value: float) -> str:
    """Turns a 0 to 1 closeness or score into a plain-language label."""
    return next(label for floor, label in MATCH_LABELS if value >= floor)

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    @staticmethod
    def _prefs(user: UserProfile) -> Dict:
        """Converts a UserProfile into the prefs dict that score_song expects."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs for a user, ranked best first."""
        # Always returns k songs, ranked: no threshold and no random pick here.
        by_id = {s.id: s for s in self.songs}
        results = recommend_songs(
            self._prefs(user), [asdict(s) for s in self.songs], k,
            min_score=0.0, explore_chance=0.0,
        )
        return [by_id[song["id"]] for song, _, _ in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns the reasons a song scored the way it did, as one string."""
        _, reasons = score_song(self._prefs(user), asdict(song))
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    numeric = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")
    songs = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for key in numeric:
                row[key] = float(row[key])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences (0 to 1).
    Numeric features score (1 - gap)**2, so mediocre matches are pushed down
    faster than close ones. Mood and genre are exact-match bonuses. Features
    missing from user_prefs are skipped and the weights renormalised.
    Required by recommend_songs() and src/main.py
    """
    total = 0.0
    used = 0.0
    reasons = []
    for feature in ("energy", "valence", "acousticness"):
        if feature in user_prefs:
            closeness = (1 - abs(user_prefs[feature] - song[feature])) ** 2
            total += WEIGHTS[feature] * closeness
            used += WEIGHTS[feature]
            reasons.append(f"{feature}: {match_label(closeness)}")
    for feature in ("mood", "genre"):
        if feature in user_prefs:
            used += WEIGHTS[feature]
            if song[feature] == user_prefs[feature]:
                total += WEIGHTS[feature]
                reasons.append(f"{feature} matches ({song[feature]})")
    return (total / used if used else 0.0, reasons)

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    min_score: float = MIN_SCORE,
    explore_chance: float = EXPLORE_CHANCE,
    rng=random,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    Returns (song_dict, score, explanation), best first.
    """
    scored = sorted(
        ((s, *score_song(user_prefs, s)) for s in songs),
        key=lambda x: x[1],
        reverse=True,
    )

    passing = [x for x in scored if x[1] >= min_score]
    if len(passing) >= MIN_MATCHES:
        picks = [(s, sc, "; ".join(r)) for s, sc, r in passing[:k]]
    else:
        picks = [
            (s, sc, "No strong match, closest option: " + "; ".join(r))
            for s, sc, r in scored[:k]
        ]

    if picks and rng.random() < explore_chance:
        chosen = {s["id"] for s, _, _ in picks}
        others = [x for x in scored if x[0]["id"] not in chosen]
        if others:
            s, sc, r = rng.choice(others)
            surprise = (s, sc, "Surprise pick: " + "; ".join(r))
            if len(picks) < k:
                picks.append(surprise)
            elif k > 1:
                picks[-1] = surprise
    return picks
