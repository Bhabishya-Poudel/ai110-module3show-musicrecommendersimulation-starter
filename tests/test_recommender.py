from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- advanced features, scoring modes and diversity ---

from src.recommender import MODES, load_songs, recommend_songs, score_song


def _song(**changes):
    base = dict(
        id=1, title="T", artist="A", genre="pop", mood="happy", energy=0.5,
        tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5,
        popularity=50, release_decade=2000, mood_tags=["warm", "cozy"],
        instrumentalness=0.5, language="en",
    )
    base.update(changes)
    return base


def test_scores_stay_between_zero_and_one_for_extreme_input():
    prefs = {"energy": 5, "popularity": 900, "release_decade": 1800, "instrumentalness": -2}
    for mode, weights in MODES.items():
        score, _ = score_song(prefs, _song(), weights)
        assert 0 <= score <= 1


def test_new_features_are_skipped_when_not_requested():
    old_style = {"genre": "pop", "mood": "happy", "energy": 0.5}
    assert score_song(old_style, _song())[0] == 1.0


def test_mood_tags_score_is_share_of_wanted_tags_found():
    one_of_two = score_song({"mood_tags": ["warm", "angry"]}, _song())[0]
    assert one_of_two == 0.5


def test_empty_prefs_raise():
    try:
        score_song({}, _song())
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_modes_change_the_ranking():
    songs = [
        _song(id=1, title="GenreMatch", genre="pop", mood="sad", energy=0.1),
        _song(id=2, title="MoodMatch", genre="rock", mood="happy", energy=0.1),
    ]
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.1}
    genre_first = recommend_songs(prefs, songs, k=2, mode="genre-first", explore_chance=0)
    mood_first = recommend_songs(prefs, songs, k=2, mode="mood-first", explore_chance=0)
    assert genre_first[0][0]["title"] == "GenreMatch"
    assert mood_first[0][0]["title"] == "MoodMatch"


def test_unknown_mode_raises():
    try:
        recommend_songs({"energy": 0.5}, [_song()], mode="nope")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_diversity_penalty_pushes_down_repeat_artist():
    songs = [
        _song(id=1, title="One", artist="Same", genre="a", energy=0.50),
        _song(id=2, title="Two", artist="Same", genre="b", energy=0.52),
        _song(id=3, title="Three", artist="Other", genre="c", energy=0.55),
    ]
    prefs = {"energy": 0.5}
    plain = recommend_songs(prefs, songs, k=3, diversity=False, explore_chance=0)
    mixed = recommend_songs(prefs, songs, k=3, diversity=True, explore_chance=0)
    assert [s["title"] for s, _, _ in plain] == ["One", "Two", "Three"]
    assert [s["title"] for s, _, _ in mixed] == ["One", "Three", "Two"]
    assert "diversity penalty" in mixed[2][2]


def test_real_catalog_loads_new_columns():
    songs = load_songs("data/songs.csv")
    assert all(0 <= s["popularity"] <= 100 for s in songs)
    assert all(isinstance(s["mood_tags"], list) and s["mood_tags"] for s in songs)
