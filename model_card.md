# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

A small recommender that finds songs by feel.

---

## 2. Goal and Intended Use

**Goal.** Suggest songs that fit a person's taste. The user gives a genre, a mood and a few numbers, like how energetic they want the music to be. The system returns the best-fitting songs, each with a reason.

**Intended use.**

- Classroom learning about how recommenders work.
- Trying out scoring rules on a tiny catalog.
- Showing how a score turns into a ranked list.

**Not intended use.**

- Real music apps or real listeners.
- Judging how good a song or an artist is.
- Learning anyone's taste from their listening history. It does not do that.
- Any case where a bad suggestion could cause harm.

**Assumptions about the user.** The user knows their taste and can state it as a genre, a mood and a few numbers. The system treats that taste as fixed.

---

## 3. How the Model Works  

Think of it as a judge holding a checklist. You tell the judge what you like: a genre, a mood, how energetic the music should be, and a few other leanings such as how upbeat or how acoustic. The judge then listens to every song in the catalog, one at a time, and gives each one a grade from 0 to 1 for how well it fits you. The songs with the best grades become your recommendations.

**What the judge looks at.** For each song it checks five things:

- **Energy:** how close the song's energy is to what you asked for. This counts the most.
- **Valence (how upbeat or positive the song sounds):** how close it is to your target. This counts second most.
- **Mood:** does the song's mood match yours exactly, like "chill" or "happy"?
- **Acousticness:** does the song sound as acoustic (or as electronic) as you like?
- **Genre:** does the song's genre match yours exactly? This counts the least.

**Close counts, but not far.** For energy, valence and acousticness, a song is rewarded for being near your target, not for being "more" or "less". A calm listener is never pushed toward loud music just because it is high energy. A song that is a little off still earns most of the credit, but one that is far off loses points quickly.

**Mood and genre are yes or no.** The label either matches or it doesn't. "Indie pop" does not count as "pop", and a word the catalog doesn't contain, like "sleepy", earns nothing.

**Turning it into a grade.** Each of the five checks is worth a share of the grade, and the shares add up to the final score. If you leave something out, say you don't give a valence, the judge skips it and judges only on what you did give, so you aren't penalized for being less specific.

**Choosing what to show.**

1. Rank every song from best grade to worst.
2. Drop songs that don't reach a basic level of fit.
3. Show the top few, each with the reasons behind its grade, such as "energy: closest match" or "mood matches (happy)". Grades are shown in words (closest, closer, close, near, distant match) instead of raw numbers, so they are easier to read.
4. If nothing fits well, show the closest songs anyway, marked as "no strong match".
5. About one time in ten, one slot is swapped for a random song, so you get a chance to find something you wouldn't have asked for.

**What I changed from the starter idea.** The common starting recipe gives a big bonus for matching genre, a smaller one for mood, and a score for energy. I turned that around. Energy and valence count the most because they describe how a song feels, and genre counts the least because it is a broad label that hides a lot of variety. I also added the "closer is better" scoring, the reasons with each pick, the "no strong match" fallback, and the surprise pick.

---

## 4. Data

- The catalog has **18 songs** in `data/songs.csv`. The starter had 10. I added 8.
- Each song has 15 fields: id, title, artist, genre, mood, energy, tempo, valence, danceability and acousticness. I added five more: popularity, release decade, mood tags, instrumentalness and language.
- The scorer uses ten of them. It ignores tempo and danceability.
- The five new fields are made up. They are not real data.
- There are **15 genres** and **14 moods**. Lofi has 3 songs and pop has 2. Every other genre has 1.
- Energy runs from 0.22 to 0.97. There are no very quiet songs.
- There is no "sad" mood. There are no lyrics, no languages and no listening history.
- The data is tiny and made up. It does not show real musical taste.

---

## 5. Strengths

- It works well for clear tastes. Chill Lofi, High-Energy Pop and Deep Intense Rock all got lists that matched my gut.
- Opposite profiles got opposite lists. Pop and lofi shared no songs.
- Every pick comes with reasons, like "mood matches (happy)". That makes the system easy to check.
- The scorer rewards closeness. A calm listener is not pushed toward loud music.
- If a user skips a feature, it is left out. They are not punished for being vague.
- Bad input is now handled. Out-of-range numbers are clamped. Empty input gives a clear error.

---

## 6. Observed Behavior and Biases

**One weakness I found: the system serves mainstream, mid-to-high-energy users better than everyone else.** The 18-song catalog has 15 genres and 14 moods, with only lofi (3 songs) and pop (2) appearing more than once, so most users can match at most one song on genre or mood. Songs also cluster in the middle of the range (energy runs only 0.22 to 0.97, and the catalog has no "sad" mood at all), so a user with extreme tastes cannot reach a high score. A mainstream pop fan can score 0.96, while a user who wants quiet, sad music (energy 0.1, valence 0.1, mood "sad") tops out at 0.60, and a user at energy 0.0 tops out at 0.61. Since the final label comes straight from the score, that second user is told "near match" at best, which looks like a bad recommender when the real problem is missing data. Squaring the gap makes this worse, because a modest energy miss is punished much harder than a small one.

---

## 7. Evaluation Process

**Summary.** I tested three normal profiles and seven tricky ones. I compared their lists side by side. I also ran one experiment: I doubled the weight on energy and halved genre.

**Note.** The scores quoted in this section come from the balanced mode before the diversity penalty was added. Run `python3 src/main.py --no-diversity` to reproduce them.

### Profiles tested

Three normal profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock) and seven adversarial ones (see below). For each I checked whether the top 5 matched what a real person with that taste would expect, and whether the order made sense.

### What surprised me

- **Gym Hero keeps showing up for "Happy Pop" fans, even though it is not a happy song.** It is an intense workout track. It lands at #3 because the scorer adds up small wins: it is pop (matches), it is very energetic (the fan wants 0.80 and it has 0.93), it is upbeat enough, and it is not acoustic, which also fits. The only thing it gets wrong is the mood ("intense" instead of "happy"), and mood is worth only 20% of the score. A song can be wrong on mood and still look good if it is right on everything else. It is #3 and not #1 because the two truly happy songs beat it comfortably (0.97 and 0.84 against 0.66).
- **The same song also shows up for rock fans.** Gym Hero is #2 for Deep Intense Rock. There its mood ("intense") matches and its energy is close, so it earns its spot. One song can be a good answer for two very different people, which tells me the catalog is small more than it tells me the song is special.
- **Adversarial profiles never produced an error, just weaker matches.** A person who wants loud, sad music still gets a list, but the top score is only 0.52, so the system is really guessing.

### Comparing profiles (what changed, and why it makes sense)

- **High-Energy Pop vs. Chill Lofi:** the pop list is loud, bright songs (Sunrise City, Rooftop Lights, Gym Hero). The lofi list is slow, quiet, acoustic ones (Library Rain, Midnight Coding, Spacewalk Thoughts). Not one song appears in both. This is the result I wanted, because these two profiles sit at opposite ends of energy and acousticness.
- **High-Energy Pop vs. Deep Intense Rock:** both want high energy, so Gym Hero and Concrete Crown appear in both lists. The difference is mood: rock wants a darker, more intense feel (valence 0.40), so Storm Runner and Iron Tide rise and the cheerful Rooftop Lights drops out. The lists overlap because the energy is shared and differ because the mood and valence are not.
- **Chill Lofi vs. Deep Intense Rock:** the most different pair, and the lists share nothing. Lofi pulls in acoustic songs like Morning Fog (folk) and Spacewalk Thoughts, while rock pulls in heavy, electric ones like Iron Tide. Energy and acousticness together separate them cleanly.
- **High-energy + sad vs. Loud + fully acoustic (adversarial):** both are impossible requests, and both put Iron Tide (metal, very loud) on top. They split after that: the "sad" profile fills the rest with intense songs (Gym Hero, Storm Runner), while the "acoustic" profile reaches for quiet folk (Morning Fog). That is reasonable, because each is trying to satisfy whichever half of the contradiction it can, but the scores (0.52 and 0.58) honestly show neither is a good match.
- **Normal pop vs. "Pop " with a typo (adversarial):** the typo version loses its genre and mood bonus and drops from 0.97 to 0.66 for the same song. Nothing is wrong with the music taste. The system only fails to read it, which is a flaw in the system.

### Adversarial profile testing

I built edge-case profiles meant to trick the scorer, then ran each one with `python3 src/main.py --adversarial` (top 5 shown). Profiles are defined in `ADVERSARIAL_PROFILES` in `src/main.py`.

What they revealed, and what I fixed:

- **Out-of-range energy (5 or -3)** produced scores above 1 and ranked the *furthest* songs first. Fixed by clamping numeric preferences to [0, 1].
- **Empty preferences** returned a list of 0.0 scores in CSV order. Now raises a `ValueError`.
- **Conflicting profiles** (high energy + sad) returned only one song because of the `MIN_SCORE` cutoff. Results are now filled up to `k` and labelled "No strong match, closest option".
- **Still open:** the catalog has no "sad" mood, so mood is ignored for that profile; genre and mood matching is exact-string, so `"Pop "` loses its bonus; a profile with only one feature can score 1.0.

Terminal output (after the fixes, balanced mode, with the diversity penalty on):

```text
Scoring mode: balanced

Conflict: high energy + sad
+---+----------------+--------------+---------------+----------------------------------------------+
| # | Title          | Artist       | Match         | Reasons                                      |
+---+----------------+--------------+---------------+----------------------------------------------+
| 1 | Iron Tide      | Black Anvil  | near match    | energy: closer match                         |
|   |                |              |               | valence: close match                         |
|   |                |              |               | acousticness: distant match                  |
+---+----------------+--------------+---------------+----------------------------------------------+
| 2 | Gym Hero       | Max Pulse    | distant match | No strong match, closest option: energy:     |
|   |                |              |               | closer match                                 |
|   |                |              |               | valence: distant match                       |
|   |                |              |               | acousticness: distant match                  |
|   |                |              |               | genre matches (pop)                          |
+---+----------------+--------------+---------------+----------------------------------------------+
| 3 | Storm Runner   | Voltline     | distant match | No strong match, closest option: energy:     |
|   |                |              |               | closest match                                |
|   |                |              |               | valence: distant match                       |
|   |                |              |               | acousticness: distant match                  |
+---+----------------+--------------+---------------+----------------------------------------------+
| 4 | Sunrise City   | Neon Echo    | distant match | No strong match, closest option: energy:     |
|   |                |              |               | close match                                  |
|   |                |              |               | valence: distant match                       |
|   |                |              |               | acousticness: distant match                  |
|   |                |              |               | genre matches (pop)                          |
|   |                |              |               | diversity penalty -0.05                      |
+---+----------------+--------------+---------------+----------------------------------------------+
| 5 | Concrete Crown | Verse Ledger | distant match | No strong match, closest option: energy:     |
|   |                |              |               | close match                                  |
|   |                |              |               | valence: distant match                       |
|   |                |              |               | acousticness: distant match                  |
+---+----------------+--------------+---------------+----------------------------------------------+


Impossible: loud + fully acoustic
+---+---------------+---------------+---------------+----------------------------------------------+
| # | Title         | Artist        | Match         | Reasons                                      |
+---+---------------+---------------+---------------+----------------------------------------------+
| 1 | Iron Tide     | Black Anvil   | near match    | energy: closer match                         |
|   |               |               |               | valence: near match                          |
|   |               |               |               | acousticness: distant match                  |
|   |               |               |               | genre matches (metal)                        |
+---+---------------+---------------+---------------+----------------------------------------------+
| 2 | Morning Fog   | Willow & Pine | distant match | No strong match, closest option: energy:     |
|   |               |               |               | distant match                                |
|   |               |               |               | valence: distant match                       |
|   |               |               |               | acousticness: closer match                   |
|   |               |               |               | mood matches (peaceful)                      |
+---+---------------+---------------+---------------+----------------------------------------------+
| 3 | Storm Runner  | Voltline      | distant match | No strong match, closest option: energy:     |
|   |               |               |               | close match                                  |
|   |               |               |               | valence: distant match                       |
|   |               |               |               | acousticness: distant match                  |
+---+---------------+---------------+---------------+----------------------------------------------+
| 4 | Pulse Horizon | Kaleido       | distant match | No strong match, closest option: energy:     |
|   |               |               |               | closer match                                 |
|   |               |               |               | valence: distant match                       |
|   |               |               |               | acousticness: distant match                  |
+---+---------------+---------------+---------------+----------------------------------------------+
| 5 | Gym Hero      | Max Pulse     | distant match | No strong match, closest option: energy:     |
|   |               |               |               | closer match                                 |
|   |               |               |               | valence: distant match                       |
|   |               |               |               | acousticness: distant match                  |
+---+---------------+---------------+---------------+----------------------------------------------+


Unknown genre and mood
+---+-------------------+----------------+---------------+----------------------------------------------+
| # | Title             | Artist         | Match         | Reasons                                      |
+---+-------------------+----------------+---------------+----------------------------------------------+
| 1 | Dusty Porch Light | Hollow Creek   | close match   | energy: closest match                        |
|   |                   |                |               | valence: close match                         |
|   |                   |                |               | acousticness: near match                     |
|   |                   |                |               | mood matches (nostalgic)                     |
+---+-------------------+----------------+---------------+----------------------------------------------+
| 2 | Velvet Hours      | Sade Marlowe   | near match    | energy: closest match                        |
|   |                   |                |               | valence: near match                          |
|   |                   |                |               | acousticness: close match                    |
+---+-------------------+----------------+---------------+----------------------------------------------+
| 3 | Midnight Coding   | LoRoom         | near match    | energy: close match                          |
|   |                   |                |               | valence: closer match                        |
|   |                   |                |               | acousticness: near match                     |
+---+-------------------+----------------+---------------+----------------------------------------------+
| 4 | Focus Flow        | LoRoom         | distant match | energy: close match                          |
|   |                   |                |               | valence: close match                         |
|   |                   |                |               | acousticness: near match                     |
|   |                   |                |               | diversity penalty -0.15                      |
+---+-------------------+----------------+---------------+----------------------------------------------+
| 5 | Library Rain      | Paper Lanterns | distant match | No strong match, closest option: energy:     |
|   |                   |                |               | close match                                  |
|   |                   |                |               | valence: close match                         |
|   |                   |                |               | acousticness: distant match                  |
+---+-------------------+----------------+---------------+----------------------------------------------+


Wrong case and whitespace
+---+----------------+---------------+------------+----------------------------------------------+
| # | Title          | Artist        | Match      | Reasons                                      |
+---+----------------+---------------+------------+----------------------------------------------+
| 1 | Sunrise City   | Neon Echo     | near match | energy: closest match                        |
|   |                |               |            | valence: closer match                        |
|   |                |               |            | acousticness: closest match                  |
+---+----------------+---------------+------------+----------------------------------------------+
| 2 | Rooftop Lights | Indigo Parade | near match | energy: closer match                         |
|   |                |               |            | valence: closest match                       |
|   |                |               |            | acousticness: close match                    |
+---+----------------+---------------+------------+----------------------------------------------+
| 3 | Concrete Crown | Verse Ledger  | near match | energy: closest match                        |
|   |                |               |            | valence: near match                          |
|   |                |               |            | acousticness: close match                    |
+---+----------------+---------------+------------+----------------------------------------------+
| 4 | Pulse Horizon  | Kaleido       | near match | energy: close match                          |
|   |                |               |            | valence: closest match                       |
|   |                |               |            | acousticness: near match                     |
+---+----------------+---------------+------------+----------------------------------------------+
| 5 | Gym Hero       | Max Pulse     | near match | energy: close match                          |
|   |                |               |            | valence: closer match                        |
|   |                |               |            | acousticness: close match                    |
|   |                |               |            | diversity penalty -0.05                      |
+---+----------------+---------------+------------+----------------------------------------------+


Out of range energy (5)
+---+----------------+---------------+---------------+----------------------------------------------+
| # | Title          | Artist        | Match         | Reasons                                      |
+---+----------------+---------------+---------------+----------------------------------------------+
| 1 | Sunrise City   | Neon Echo     | closer match  | energy: near match                           |
|   |                |               |               | valence: closer match                        |
|   |                |               |               | acousticness: closest match                  |
|   |                |               |               | mood matches (happy)                         |
|   |                |               |               | genre matches (pop)                          |
+---+----------------+---------------+---------------+----------------------------------------------+
| 2 | Rooftop Lights | Indigo Parade | close match   | energy: near match                           |
|   |                |               |               | valence: closest match                       |
|   |                |               |               | acousticness: close match                    |
|   |                |               |               | mood matches (happy)                         |
+---+----------------+---------------+---------------+----------------------------------------------+
| 3 | Gym Hero       | Max Pulse     | near match    | energy: closer match                         |
|   |                |               |               | valence: closer match                        |
|   |                |               |               | acousticness: close match                    |
|   |                |               |               | genre matches (pop)                          |
|   |                |               |               | diversity penalty -0.05                      |
+---+----------------+---------------+---------------+----------------------------------------------+
| 4 | Pulse Horizon  | Kaleido       | near match    | energy: closer match                         |
|   |                |               |               | valence: closest match                       |
|   |                |               |               | acousticness: near match                     |
+---+----------------+---------------+---------------+----------------------------------------------+
| 5 | Storm Runner   | Voltline      | distant match | No strong match, closest option: energy:     |
|   |                |               |               | close match                                  |
|   |                |               |               | valence: distant match                       |
|   |                |               |               | acousticness: close match                    |
+---+----------------+---------------+---------------+----------------------------------------------+


Only genre given
+---+---------------------+----------------+---------------+----------------------------------------------+
| # | Title               | Artist         | Match         | Reasons                                      |
+---+---------------------+----------------+---------------+----------------------------------------------+
| 1 | Coffee Shop Stories | Slow Stereo    | closest match | genre matches (jazz)                         |
+---+---------------------+----------------+---------------+----------------------------------------------+
| 2 | Sunrise City        | Neon Echo      | distant match | No strong match, closest option:             |
+---+---------------------+----------------+---------------+----------------------------------------------+
| 3 | Midnight Coding     | LoRoom         | distant match | No strong match, closest option:             |
+---+---------------------+----------------+---------------+----------------------------------------------+
| 4 | Storm Runner        | Voltline       | distant match | No strong match, closest option:             |
+---+---------------------+----------------+---------------+----------------------------------------------+
| 5 | Library Rain        | Paper Lanterns | distant match | No strong match, closest option: diversity   |
|   |                     |                |               | penalty -0.05                                |
+---+---------------------+----------------+---------------+----------------------------------------------+


Dead center (0.5 everywhere)
+---+-------------------+--------------+-------------+----------------------------------------------+
| # | Title             | Artist       | Match       | Reasons                                      |
+---+-------------------+--------------+-------------+----------------------------------------------+
| 1 | Velvet Hours      | Sade Marlowe | close match | energy: closest match                        |
|   |                   |              |             | valence: near match                          |
|   |                   |              |             | acousticness: close match                    |
+---+-------------------+--------------+-------------+----------------------------------------------+
| 2 | Midnight Coding   | LoRoom       | close match | energy: close match                          |
|   |                   |              |             | valence: closer match                        |
|   |                   |              |             | acousticness: near match                     |
+---+-------------------+--------------+-------------+----------------------------------------------+
| 3 | Dusty Porch Light | Hollow Creek | close match | energy: closest match                        |
|   |                   |              |             | valence: close match                         |
|   |                   |              |             | acousticness: near match                     |
+---+-------------------+--------------+-------------+----------------------------------------------+
| 4 | Night Drive Loop  | Neon Echo    | close match | energy: near match                           |
|   |                   |              |             | valence: closest match                       |
|   |                   |              |             | acousticness: near match                     |
+---+-------------------+--------------+-------------+----------------------------------------------+
| 5 | Island Breeze     | Sol Roots    | near match  | energy: close match                          |
|   |                   |              |             | valence: distant match                       |
|   |                   |              |             | acousticness: closer match                   |
+---+-------------------+--------------+-------------+----------------------------------------------+
```

---

## 8. Ideas for Improvement

1. **Add more songs.** Aim for 100 or more. Cover sad and very quiet music. Then every user type can get a strong match.
2. **Make mood and genre fuzzy.** Treat "indie pop" as close to "pop". Ignore case and spaces. Warn when a word is not in the catalog.
3. **Mix up the top results.** Do not show five songs from the same corner. Add variety on purpose.

---

## 9. Personal Reflection

**Biggest learning moment.** I found that one bad input could break the whole scale. An energy of 5 gave scores above 1, and the furthest songs ranked first. A score is only useful if it stays inside its range.

**Checking my work.** I did not trust the output until I ran it. Running odd profiles found three real bugs. I fixed them and ran the profiles again. I also checked every number I wrote in this card against the run output.

**What surprised me.** Simple adding and weighing still feels like a recommendation. Gym Hero showing up for Happy Pop fans felt almost human, like a friend guessing wrong. It was just small wins adding up. Showing reasons made the picks feel smarter than they are.

**What I would try next.** Add many more songs. Let users rate picks, so the system can learn. Make mood and genre fuzzy. Test a profile with two tastes at once, like lofi and metal.
