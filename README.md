# 🎵 Music Recommender Simulation

## Project Summary

This is a small music recommender. You give it a genre, a mood and a few numbers, like energy and acousticness. It scores all 18 songs in the catalog and shows the best matches, each with a reason. See the [model card](model_card.md) for details.

---

## How The System Works

- **Song features:** id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability and acousticness. Scoring uses energy, valence, mood, acousticness and genre.
- **UserProfile:** favorite genre, favorite mood, target energy, and whether they like acoustic music.
- **Scoring:** each song gets a 0 to 1 score. Energy, valence and acousticness score `(1 - gap)²`, where gap is the distance from the user's target. Mood and genre add a bonus on an exact match. Weights: energy 0.35, valence 0.25, mood 0.20, acousticness 0.10, genre 0.10. In the output, closeness and the final score are shown as labels instead of raw numbers: **closest match** (0.95+), **closer match** (0.85+), **close match** (0.70+), **near match** (0.50+) and **distant match** (below 0.50).
- **Choosing songs:** sort by score, keep songs scoring at least 0.5, and return the top k. If none qualify, return the closest songs with a "no strong match" note. About 1 time in 10, one slot becomes a random surprise pick.

**Data flow: Input → Process → Output.**

```
INPUT                    PROCESS (the loop)                          OUTPUT
─────                    ──────────────────                          ──────
user_prefs         ┌───► for each song in songs.csv:                 Top K list
{genre: "lofi",    │       score_song(prefs, song) ──► (score, why)  [(song, score, why),
 mood: "chill",    │                                                  (song, score, why),
 energy: 0.4}      │     ┌─ energy/valence/acoustic: (1-gap)² × weight   ...]
                   │     ├─ mood match?  +0.20
songs.csv ─────────┘     ├─ genre match? +0.10
 (load_songs →           └─ ÷ weights actually used  → 0..1
  list of dicts)                      │
                                      ▼
                         sort all songs by score, high → low
                                      ▼
                         keep score ≥ 0.5  (else "no strong match" fallback)
                                      ▼
                         take top k  (~10% chance: swap last for a surprise pick)
```

*One song's trip.* Say the user wants lofi, chill, energy 0.4, and a song is lofi, chill, energy 0.35:

1. `load_songs` turns the CSV row into a dict with numeric fields as floats.
2. Energy gap is 0.05, so closeness is (0.95)² ≈ 0.90, adding 0.35 × 0.90 = 0.315.
3. Mood and genre both match exactly, adding 0.20 + 0.10 = 0.30.
4. Valence and acousticness weren't given, so they are skipped. Weights used are 0.65, so the score is (0.315 + 0.30) / 0.65 ≈ 0.95.
5. The song keeps its "why" strings with the score, and after every song is scored the list is sorted and cut to the top k.

Every song is scored independently, and ranking is the only step that compares songs. The threshold and surprise pick only change what is shown, not how songs are scored.

**Algorithm Recipe (final).**

| Step | Rule | Weight |
|---|---|---|
| Energy | `(1 - gap)²`, gap = distance from target energy | 0.35 |
| Valence | `(1 - gap)²` (only if the user gives a target) | 0.25 |
| Mood | exact match = full weight, otherwise 0 | 0.20 |
| Acousticness | `(1 - gap)²`, target 0.8 if the user likes acoustic, else 0.2 | 0.10 |
| Genre | exact match = full weight, otherwise 0 | 0.10 |
| Mood tags | share of the wanted tags the song has | 0.10 |
| Instrumentalness, popularity, decade | `(1 - gap)²`, only if asked for | 0.05 each |
| Language | exact match | 0.05 |
| Normalize | `total / sum of weights actually used`, giving a 0 to 1 score | |
| Rank | sort high to low, keep score ≥ 0.5, return top k, about 10% chance one slot is a surprise pick | |

This differs from the common starting recipe (+2.0 genre, +1.0 mood, energy similarity). I use normalized 0 to 1 weights, put energy first, and weight mood above genre, because mood describes how a song feels while genre is a broad label.

**Expected biases.**

- **Energy dominates.** At 0.35 it is the biggest factor, so a song with the right energy but the wrong mood and genre can outrank a song that matches both. Great mood matches with a slightly different energy may be buried.
- **Genre is under-weighted.** At 0.10 it barely moves the ranking, so a listener who really cares about genre (for example, only jazz) may still see other genres.
- **Exact-match only for mood and genre.** "Indie pop" does not match "pop", and a typed word like "sleepy" matches nothing. Close labels get zero credit, which punishes users who describe taste in different words.
- **Small, uneven catalog.** Only 18 songs, and lofi has 3 while most genres have 1. Lofi fans get more choice and the rest get a thin list that often falls back to "no strong match".
- **Low-energy edge.** The lowest song energy is 0.22, so a user who asks for energy near 0 can never score a near-perfect match.
- **Acousticness is a guess.** A yes/no preference becomes 0.8 or 0.2, which ignores users in the middle.
- **Content-only.** With no data from other listeners, the system can't learn taste from behavior and tends to repeat what the features already say.

**Real-world recommendations and my version.** Services like Spotify and Apple Music blend two ideas: collaborative filtering, which predicts your taste from what similar listeners play, skip and save, and content-based filtering, which matches the features of songs you already like (energy, mood, tempo and so on). My version is purely content-based, since I have no data from other users. It scores each song by how *close* it is to the user's targets, not by "more is better", so a calm lofi listener is never pushed toward high-energy tracks. Energy matters most, then valence, then a mood match, with acousticness and genre as smaller bonuses. Songs below a minimum score are dropped, the closest songs are shown with a "no strong match" note if nothing qualifies, and about 1 time in 10 a random surprise pick is added to help users discover something new.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Scoring modes and options

```bash
python3 src/main.py --mode genre-first      # also: mood-first, energy-focused, balanced (default)
python3 src/main.py --no-diversity          # turn off the diversity penalty
python3 src/main.py --adversarial           # run the edge-case profiles
```

Each mode is a different weight table in `MODES` in `src/recommender.py`. Songs also have five extra features: popularity, release decade, mood tags, instrumentalness and language. A profile can ask for any of them. Features a profile leaves out are skipped. By default, a song loses 0.10 for each earlier pick by the same artist and 0.05 for each earlier pick in the same genre.

### Running Tests

Run the tests with:

```bash
pytest
```

---

## Sample Recommendation Output

Profile: genre=pop, mood=happy, energy=0.80, valence=0.82, acousticness=0.20

Generated with `python src/main.py` from the project root. Scores appear as match labels (see Scoring above). The last line of reasons for Gym Hero shows the diversity penalty.

```text
High-Energy Pop
+---+----------------+---------------+---------------+----------------------------------------------+
| # | Title          | Artist        | Match         | Reasons                                      |
+---+----------------+---------------+---------------+----------------------------------------------+
| 1 | Sunrise City   | Neon Echo     | closest match | energy: closest match                        |
|   |                |               |               | valence: closest match                       |
|   |                |               |               | acousticness: closest match                  |
|   |                |               |               | mood matches (happy)                         |
|   |                |               |               | genre matches (pop)                          |
+---+----------------+---------------+---------------+----------------------------------------------+
| 2 | Rooftop Lights | Indigo Parade | close match   | energy: closer match                         |
|   |                |               |               | valence: closest match                       |
|   |                |               |               | acousticness: close match                    |
|   |                |               |               | mood matches (happy)                         |
+---+----------------+---------------+---------------+----------------------------------------------+
| 3 | Gym Hero       | Max Pulse     | near match    | energy: close match                          |
|   |                |               |               | valence: closer match                        |
|   |                |               |               | acousticness: close match                    |
|   |                |               |               | genre matches (pop)                          |
|   |                |               |               | diversity penalty -0.05                      |
+---+----------------+---------------+---------------+----------------------------------------------+
| 4 | Concrete Crown | Verse Ledger  | near match    | energy: closest match                        |
|   |                |               |               | valence: near match                          |
|   |                |               |               | acousticness: close match                    |
+---+----------------+---------------+---------------+----------------------------------------------+
| 5 | Pulse Horizon  | Kaleido       | near match    | energy: close match                          |
|   |                |               |               | valence: closest match                       |
|   |                |               |               | acousticness: near match                     |
+---+----------------+---------------+---------------+----------------------------------------------+
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Weight shift: double energy, halve genre

Changed `WEIGHTS` from energy 0.35 / genre 0.10 to energy 0.70 / genre 0.05 (valence, mood, acousticness unchanged). The weights no longer sum to 1 (they sum to 1.30), but `score_song` divides by the weights in use, so every score stayed within 0 to 1. I checked this for all 18 songs under all three profiles.

What changed (top 5):

- **High-Energy Pop:** Sunrise City and Rooftop Lights stayed #1 and #2. Concrete Crown (hip hop) overtook Gym Hero (pop) for #3, because Gym Hero's genre match is worth half as much. Night Drive Loop replaced Pulse Horizon at #5.
- **Chill Lofi:** same top 4 order. Coffee Shop Stories (jazz) replaced Morning Fog at #5.
- **Deep Intense Rock:** Storm Runner stayed #1. Iron Tide (metal/angry) moved above the weaker matches, and Pulse Horizon (edm) entered the top 5.

Verdict: **different, not clearly more accurate.** The top picks did not move, which suggests they are driven by several features agreeing. Slots 3 to 5 reshuffled toward songs with similar energy but the wrong genre, and scores in the tail rose (for example 0.57 to 0.65), so the system separates good matches from weak ones less sharply. I reverted to the original weights.

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

- The catalog is tiny, with 18 songs.
- Most genres and moods have only one song.
- There is no "sad" mood, and no very quiet songs.
- It does not understand lyrics or language.
- Mood and genre must match exactly.
- Mainstream, mid-energy tastes get the best matches.

More detail is in the model card.

---

## Reflection

Read the full [**Model Card**](model_card.md).

Simple scores can feel like real recommendations. Every song gets a grade, and the grades make a list. The weights decide whose taste the list fits. A tiny catalog also decides that. Users with unusual tastes get weaker matches, and nothing in the score tells them why.
