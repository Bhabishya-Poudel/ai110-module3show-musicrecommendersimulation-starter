# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
