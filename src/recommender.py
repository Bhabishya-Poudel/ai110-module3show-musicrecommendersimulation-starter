import csv
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field

WEIGHTS = {
    "energy": 0.35, "valence": 0.25, "mood": 0.20, "acousticness": 0.10, "genre": 0.10,
    "mood_tags": 0.10, "instrumentalness": 0.05, "popularity": 0.05,
    "release_decade": 0.05, "language": 0.05,
}

# Scoring modes (Strategy pattern): each mode is just a different weight table.
# recommend_songs() takes a mode name and hands the weights to score_song().
MODES = {
    "balanced": WEIGHTS,
    "genre-first": {**WEIGHTS, "genre": 0.60, "mood": 0.15, "energy": 0.20, "valence": 0.10},
    "mood-first": {**WEIGHTS, "mood": 0.45, "mood_tags": 0.25, "valence": 0.20, "energy": 0.15, "genre": 0.05},
    "energy-focused": {**WEIGHTS, "energy": 0.70, "valence": 0.15, "mood": 0.10, "genre": 0.05},
}

# Numeric features: (lowest value, span). A gap is the distance divided by the span.
NUMERIC = {
    "energy": (0.0, 1.0),
    "valence": (0.0, 1.0),
    "acousticness": (0.0, 1.0),
    "instrumentalness": (0.0, 1.0),
    "popularity": (0.0, 100.0),
    "release_decade": (1960.0, 60.0),
}
EXACT = ("mood", "genre", "language")

ARTIST_PENALTY = 0.10  # taken off a song's score for each pick already by the same artist
GENRE_PENALTY = 0.05   # taken off for each pick already in the same genre
MIN_SCORE = 0.5      # songs scoring below this are not a real match
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
    popularity: float = 50.0
    release_decade: int = 2020
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    language: str = "en"

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
            min_score=0.0, explore_chance=0.0, diversity=False,
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
    numeric = (
        "energy", "tempo_bpm", "valence", "danceability", "acousticness",
        "popularity", "release_decade", "instrumentalness",
    )
    songs = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for key in numeric:
                row[key] = float(row[key])
            row["mood_tags"] = [t for t in row["mood_tags"].split("|") if t]
            songs.append(row)
    return songs

def score_song(
    user_prefs: Dict, song: Dict, weights: Optional[Dict] = None
) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences (0 to 1).
    Numeric features score (1 - gap)**2, so mediocre matches are pushed down
    faster than close ones. Mood, genre and language are exact-match bonuses.
    mood_tags scores the share of the wanted tags the song has. Features
    missing from user_prefs are skipped and the weights renormalised.
    Numeric preferences are clamped to the feature's range so the score stays
    in 0 to 1. Raises ValueError if user_prefs has no usable feature.
    weights picks the scoring mode (defaults to WEIGHTS).
    Required by recommend_songs() and src/main.py
    """
    weights = weights or WEIGHTS
    total = 0.0
    used = 0.0
    reasons = []
    for feature, (low, span) in NUMERIC.items():
        if feature in user_prefs:
            wanted = min(low + span, max(low, user_prefs[feature]))
            gap = min(1.0, abs(wanted - song[feature]) / span)
            closeness = (1 - gap) ** 2
            total += weights[feature] * closeness
            used += weights[feature]
            reasons.append(f"{feature}: {match_label(closeness)}")
    if user_prefs.get("mood_tags"):
        wanted_tags = set(user_prefs["mood_tags"])
        hits = wanted_tags & set(song["mood_tags"])
        total += weights["mood_tags"] * len(hits) / len(wanted_tags)
        used += weights["mood_tags"]
        if hits:
            reasons.append(f"mood tags match ({', '.join(sorted(hits))})")
    for feature in EXACT:
        if feature in user_prefs:
            used += weights[feature]
            if song[feature] == user_prefs[feature]:
                total += weights[feature]
                reasons.append(f"{feature} matches ({song[feature]})")
    if not used:
        raise ValueError(
            "user_prefs needs at least one of: " + ", ".join([*NUMERIC, "mood_tags", *EXACT])
        )
    return (total / used, reasons)

def _pick_diverse(candidates: List[Tuple], k: int, diversity: bool) -> List[Tuple]:
    """
    Greedily picks k (song, score, reasons) tuples. With diversity on, each pick
    costs later songs ARTIST_PENALTY (same artist) and GENRE_PENALTY (same genre).
    Returns (song, adjusted score, reasons) with the penalty added to the reasons.
    """
    left = list(candidates)
    picked: List[Tuple] = []
    while left and len(picked) < k:
        best = None
        for s, sc, r in left:
            penalty = 0.0
            if diversity:
                penalty += ARTIST_PENALTY * sum(p[0]["artist"] == s["artist"] for p in picked)
                penalty += GENRE_PENALTY * sum(p[0]["genre"] == s["genre"] for p in picked)
            adjusted = max(0.0, sc - penalty)
            if best is None or adjusted > best[1]:
                best = (s, adjusted, r, penalty)
        left = [x for x in left if x[0]["id"] != best[0]["id"]]
        reasons = best[2] + ([f"diversity penalty -{best[3]:.2f}"] if best[3] else [])
        picked.append((best[0], best[1], reasons))
    return picked

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    min_score: float = MIN_SCORE,
    explore_chance: float = EXPLORE_CHANCE,
    rng=random,
    mode: str = "balanced",
    diversity: bool = True,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    mode picks a weight table from MODES. diversity penalises repeat artists
    and genres in the top k. Returns (song_dict, score, explanation), best first.
    """
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}, choose from: {', '.join(MODES)}")
    weights = MODES[mode]
    scored = sorted(
        ((s, *score_song(user_prefs, s, weights)) for s in songs),
        key=lambda x: x[1],
        reverse=True,
    )

    passing = [x for x in scored if x[1] >= min_score]
    picks = _pick_diverse(passing, k, diversity)
    picks = [(s, sc, "; ".join(r)) for s, sc, r in picks]
    if len(picks) < k:
        # Not enough real matches: fill the rest with the closest remaining songs, labelled.
        rest = _pick_diverse(scored[len(passing):], k - len(picks), diversity)
        picks += [
            (s, sc, "No strong match, closest option: " + "; ".join(r))
            for s, sc, r in rest
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
