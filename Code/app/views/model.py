"""How well the predictions held up, and what the models lean on. Numbers from step 5, test year 2025."""

import streamlit as st

from common import GLOSS_LINE, current_floor, explain, footer, header, sidebar_watchlist

header("The Model")
floor = current_floor()

explain("The model page", """
The size floor slider does not affect this page. It explains what the two chances on The List mean,
how we tested them on a year the models had never seen, and where they are strong and weak.
""")

# ---- 1. what we predict ----------------------------------------------------------------
st.markdown("### Two questions about next year")
st.markdown(f"""
Every year-end, the rules give each brand one of four labels: **discontinued, declining, stable, growing**.
They are about shelf space more than sales: {GLOSS_LINE}.
The model does not predict the label. It answers two yes/no questions about where the brand will be a year from now:

| | The question | Yes means |
|---|---|---|
| **Viable next year?** | Will it still be worth carrying? | Stable *or* growing a year from now |
| **Growing next year?** | Will it be taking off? | Growing a year from now |

Growing is part of viable: every growing brand is viable, but most viable brands are just stable.
So the viable chance is never the smaller of the two numbers. They are separate models, so on a handful of brands
growing came out a point or two higher; there, viable is lifted to match.

**How to read a chance.** "Growing 0.65" means: of 100 brands that looked like this one, about 65 were growing a year
later. Use it as a ranking. Sort by it, take the top of the list, and go look at those brands.
""")

# ---- 2. how we tested ----------------------------------------------------------------
st.markdown("### How we tested it")
st.markdown("""
A test the models could not cheat on. Learn from 2022, 2023 and 2024. Stand at the end of 2024 and predict
the end of 2025. Then open 2025 and count how many were right. The models never saw 2025 while learning.

The score: **of the 100 brands each approach was most sure about, how many were right a year later?**
""")
st.markdown("""
| | Random picking | "Stays the same" | "Last year's growth alone" | Simple model | Boosted model |
|---|---|---|---|---|---|
| **Viable next year?** | 43 | 84 | 61 | **98** | 95 |
| **Growing next year?** | 8 | 53 | 19 | 51 | **66** |
""")
st.caption("Tested with a 250-case floor. The app uses the simple model for viable and the boosted model for growing.")

with st.expander("What the five approaches are"):
    st.markdown("""
Think of five people each handing you a list of 100 brands at the end of 2024.

- **Random picking.** Close your eyes and point at 100 brands. Anything that can't beat this is useless.
- **"Stays the same."** Guess that whatever a brand is today, it will be the same next year. This is the bar the models have to clear to be worth using, and they do: 98 vs 84 on viable, 66 vs 53 on growing.
- **"Last year's growth alone."** Look at one number only: did sales go up last year. The original starting idea.
- **Simple model.** Logistic regression over thirteen facts about each brand (sales and shelf vs its best, shelf vs a year ago, shelf now, size, age, sales vs a year ago, momentum, the category's sales change and the brand's sales against it, today's label, category, price tier).
- **Boosted model.** Gradient boosting; can learn things like "small brands behave differently from big ones."

We show all five because "98 right" means nothing without "compared to what."
""")

# ---- 3. the two takeaways ----------------------------------------------------------------
st.markdown("### What to take from it")
st.markdown("""
**Survival is predictable.** A brand still in most of the stores it ever had almost always survives.
98 of the simple model's top 100 were still viable a year later, and 7 to 10 of its top 10 in every category.

**Growth is harder, and we say so.** Today's growing brands keep growing about half the time (53 of 100).
The best model gets 66 of 100. Better at the top of the list, not a different world.

**Last year's sales growth alone predicts neither.** The signal is in shelf and in how close a brand
is to its best, not in last year's growth rate.
""")

# ---- 4. what the models lean on ----------------------------------------------------------------
st.markdown("### What the models lean on")
st.markdown("""
| Input | Viable next year? | Growing next year? |
|---|---|---|
| Shelf vs its best | **strongest by far** | second |
| Sales vs its best | small | **strongest by far** |
| Brand size | second | small |
| Momentum (quarters in a row near its best) | small | third |
| Sales vs a year ago | small | small |
| Brand vs its category (added Nov 2026) | near zero | near zero |
| Category, price tier | near zero | near zero |

In one line: **survival is about shelf, growth is about sales momentum.**

**About "vs its category."** Eurpac asked whether a brand's growth relative to its category should feed the
prediction. We built it (each brand's growth divided by its category's growth over established brands) and it is
on The List and One Brand. It did not change the model's accuracy: once the model knows how a brand is doing
against its own history, how its category did adds almost nothing. It is still useful context for a person reading
the list.
""")

# ---- 5. by category ----------------------------------------------------------------
st.markdown("### Strong and weak, by category")
st.caption("Of the 10 brands the model was most sure about in each category, how many were right a year later.")
cat_rows = [("Vodka", 9, 10), ("Tequila", 10, 9), ("Prepared cocktails", 10, 5), ("Whiskey", 10, 5), ("Cordials", 10, 6),
            ("Gin", 10, 6), ("Rum", 9, 6), ("Non-alcoholic spirits", 10, 4), ("Brandy", 7, 3), ("Cognac", 8, 2), ("Grain alcohol", 8, 2)]
pick = st.multiselect("Categories", [r[0] for r in cat_rows], default=[], placeholder="All categories")
shown = [r for r in cat_rows if not pick or r[0] in pick]
st.markdown("| Category | Viable? (of 10) | Growing? (of 10) |\n|---|---|---|\n" +
            "\n".join(f"| {c} | {v} | {g} |" for c, v, g in shown))
st.markdown("Survival is reliable everywhere. Growth is reliable in vodka and tequila, fair in the middle, and weak in "
            "brandy, cognac and grain alcohol (small categories with few growing brands).")

# ---- 6. the floor ----------------------------------------------------------------
st.markdown("### The size floor")
st.markdown(f"""
The models were tested with a floor of **250 cases a year** (about five a week), because tiny brands are always
"at their best" and flood the top of the growing list. The slider on Home and The List changes which brands
you see; it does not change what the models learned. Yours is set to **{floor}**.

**What if the models used 500?** We retrained and retested at 500. Viable: 98 of the top 100 either way.
Growing: 60 of the top 100 at 500 versus 66 at 250, and worse in most categories. Raising the training floor
removes brands but does not make the predictions better, so the models stay at 250. The slider opens at 500
because that is the size Eurpac prefers to look at; that is a viewing choice, and the slider moves either way.
""")
with st.expander("How many brands each floor keeps"):
    st.markdown("""
| Floor (cases a year) | Brands kept |
|---|---|
| 12 | about 12,500 |
| 52 | about 9,300 |
| 100 | about 7,800 |
| 250 (tested) | about 5,700 |
| 500 | about 4,300 |
""")

sidebar_watchlist()
footer()
