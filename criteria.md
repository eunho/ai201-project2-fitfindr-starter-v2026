# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
Our search relies on keyword overlap and regex query parsing, which might occasionally fail to match an ambiguously phrased query, or an upstream LLM call may encounter rate-limit pacing or intermittent network latency. Expecting 4 of 5 (80%) accounts for realistic search variation and model call retries while ensuring high overall reliability.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
Unlike natural language generation, the early-stopping branch in `agent.py::run_agent` is deterministic code logic evaluating `if not session["search_results"]`. Because there is zero model uncertainty involved in deciding whether an empty list was returned, a failure here represents a pure logic bug; hence 5 of 5 (100%) must succeed.

---

## 3. Session state preserves selected item across tool calls

In 5 of 5 runs where search returns results, the item ID in `session['selected_item']['id']` matches exactly the listing ID passed as `new_item` into `suggest_outfit` and `create_fit_card`.

**Why this target:**
Session state propagation is deterministic Python dictionary assignment within process memory. Once an item is selected from `session['search_results']`, passing it into subsequent tool arguments should never drop, overwrite, or mutate the item ID, so anything less than 5 of 5 indicates a critical state management bug.

---

## 4. Fit card includes price, platform, and proper length

In at least 4 of 5 successful runs, the generated fit card contains both the listing's price (formatted with a dollar sign) and the platform name, and is between 2 and 4 sentences long.

**Why this target:**
`create_fit_card` calls an LLM with temperature 0.9 to generate natural, creative captions rather than rigid templates. While the prompt explicitly instructs the model to include the price, platform, and write 2–4 sentences, high-temperature generation can occasionally produce a single-sentence punchline or omit a token. Setting 4 of 5 allows for natural LLM phrasing variance while enforcing consistent quality.

---

## 5. Search strictly respects price ceilings

Given a query specifying a maximum price ceiling, in 5 of 5 runs where an item is found, the price of `session['selected_item']['price']` is less than or equal to the specified price ceiling.

**Why this target:**
Price ceiling filtering is a strict mathematical inequality (`item['price'] <= max_price`) enforced directly in `search_listings`. Since candidate filtering does not depend on probabilistic model decisions, returning any item over the user's budget is unacceptable and must hold across 5 of 5 runs.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
