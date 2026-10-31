# AI Interactions Log

Stretch challenges 1 to 4. Each section lists the prompt, what the assistant changed, and what was checked by running the code.

---

## Agentic Workflow (SF8): Advanced Song Features (Challenge 1)

**What task did you give the agent?**

Add 5 or more new song attributes to `data/songs.csv`, and update the scoring in `src/recommender.py` so they count.

**Prompts used:**

> Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags. Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes.

**What did the agent generate or change?**

- `data/songs.csv`: five new columns for all 18 songs.
  - `popularity` (0 to 100)
  - `release_decade` (1970 to 2020)
  - `mood_tags` (pipe-separated, like `nostalgic|warm|cozy`)
  - `instrumentalness` (0 to 1)
  - `language` (`en`, `es`, or `none` for instrumentals)
- `src/recommender.py`:
  - `Song` has the new fields with defaults, so older code and tests still build songs the same way.
  - `load_songs` reads the new numbers and splits `mood_tags` into a list.
  - `score_song` now uses a `NUMERIC` table (low value and span per feature). Popularity and decade use the same `(1 - gap)^2` rule, with the gap divided by the feature's span.
  - `mood_tags` scores the share of wanted tags the song has.
  - `language` is an exact match, like mood and genre.
  - All new weights are small (0.05 to 0.10). A user who does not ask for a feature skips it, so old profiles score the same as before.
- `src/main.py`: a new "Throwback Acoustic" profile that uses every new feature.
- `tests/test_recommender.py`: tests for the new scoring.

**What did you verify or fix manually?**

- Re-ran the three original profiles. Their scores did not change, because unused features are skipped.
- Checked scores stay between 0 and 1 for extreme input (popularity 900, decade 1800, energy 5).
- Checked the new profile by hand. Morning Fog (1970) scores "distant match" on decade for a 1990 target, because the gap is 20 years out of 60. That is the intended result.
- The catalog dates and tags are made up. They are not real data.

---

## Design Pattern (SF10): Scoring Modes (Challenge 2)

**Which design pattern did you use?**

A simple **Strategy** pattern. Each scoring mode is a weight table, and the ranking code stays the same.

**How did AI help you brainstorm or implement it?**

Prompt: *"Brainstorm a simple design pattern, like Strategy, that keeps the code modular so a user can switch between ranking modes in main.py."*

Options that came up:

1. A class per mode with its own `score` method. Flexible, but a lot of code for what differs only by weights.
2. A `MODES` dictionary of weight tables. The only thing that differs between modes is how much each feature counts, so this is the smallest design that works.
3. If-statements on the mode name inside `score_song`. Quick, but every new mode means editing the scorer.

I chose option 2. It keeps `score_song` and `recommend_songs` unchanged for every mode, and a new mode is one line.

**How does the pattern appear in your final code?**

- `MODES` in `src/recommender.py`: `balanced`, `genre-first`, `mood-first`, `energy-focused`.
- `score_song(..., weights)` takes the strategy as an argument.
- `recommend_songs(..., mode="balanced")` looks up the weights and rejects unknown modes.
- `python3 src/main.py --mode mood-first` switches modes.

Manual check: for a pop and happy listener, genre-first puts Gym Hero (pop, intense) second, while mood-first keeps the happy songs on top. A test builds two songs, one that matches on genre and one on mood, and checks that each mode ranks them the way its name says.

I did not use a separate branch for the experiment. The modes only add data, so nothing on the working version was at risk.

---

## Diversity and Fairness (Challenge 3)

**Prompt used:**

> Add a diversity penalty. If a song's artist is already in the top recommendations list, subtract from its score. Do the same, with a smaller amount, when its genre is already there. Pick songs one at a time, so each pick changes the next song's score.

**What was generated:**

- `_pick_diverse` in `src/recommender.py` picks greedily. Each earlier pick by the same artist costs `ARTIST_PENALTY` (0.10). Each earlier pick in the same genre costs `GENRE_PENALTY` (0.05).
- The penalty shows up in the reasons, like `diversity penalty -0.05`.
- `diversity=False` and `--no-diversity` turn it off. `Recommender.recommend` keeps it off so it still returns a plain ranking.

**Manual check:** a test with two songs by the same artist and one by another. With the penalty off the order is One, Two, Three. With it on, Three moves ahead of Two. My first version of that test failed. The test data was wrong, not the code, because a 0.10 penalty is not enough to beat a song that is much closer. I changed the numbers and kept the penalty small on purpose.

---

## Visual Summary Table (Challenge 4)

**Prompt used:**

> Show the top recommendations as a formatted table in the terminal. It must include the reasons for each score.

**What was generated:** `format_table` in `src/main.py`. It uses plain ASCII, not `tabulate`, so no new install is needed. The columns are rank, title, artist, overall match and reasons, with one reason per line.

**Manual check:** my first version joined the reasons with `|`, which looked like table borders. I changed it to one reason per line.
