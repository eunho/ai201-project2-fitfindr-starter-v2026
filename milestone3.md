# Milestone 3 — Acceptance Criteria Testing Analysis

## The Three Written Criteria (Sentences Only)

- **Criterion 3:** In 5 of 5 runs where search returns results, the item ID in `session['selected_item']['id']` matches exactly the listing ID passed as `new_item` into `suggest_outfit` and `create_fit_card`.
- **Criterion 4:** In at least 4 of 5 successful runs, the generated fit card contains both the listing's price (formatted with a dollar sign) and the platform name, and is between 2 and 4 sentences long.
- **Criterion 5:** Given a query specifying a maximum price ceiling, in 5 of 5 runs where an item is found, the price of `session['selected_item']['price']` is less than or equal to the specified price ceiling.

---

## Testing Procedure For Each of the Five Acceptance Criteria

### 1. "Given a query that matches at least one listing, the agent completes all three tool calls and returns a fit card — in at least 4 of 5 tries."

**How to test:**
1. Execute `run_agent(query, wardrobe)` 5 times using a known matching query (e.g., `'vintage graphic tee under $30'`).
2. For each run, inspect the execution trace or call count to verify that `search_listings`, `suggest_outfit`, and `create_fit_card` were each called in order.
3. Check that the returned `session['fit_card']` is a non-empty string.
4. Count the number of runs where all three tools completed and a fit card string was returned.
5. **Pass condition:** Count is >= 4 out of 5.

---

### 2. "Given a query that matches no listings, the agent stops before calling suggest_outfit and returns a message naming what to change — 5 of 5 tries."

**How to test:**
1. Execute `run_agent(query, wardrobe)` 5 times using an impossible query known to match no catalog listings (e.g., `'designer ballgown size XXS under $5'`).
2. For each run, verify from the execution trace or mock call tracker that `suggest_outfit` was called 0 times.
3. Verify that `session['fit_card']` is `None` and `session['outfit_suggestion']` is `None`.
4. Inspect `session['error']` to confirm it contains a non-empty descriptive message identifying what parameter to adjust (e.g., "try raising the price ceiling or changing keywords").
5. **Pass condition:** All 5 runs halt before `suggest_outfit` and supply the corrective error message.

---

### 3. "In 5 of 5 runs where search returns results, the item ID in `session['selected_item']['id']` matches exactly the listing ID passed as `new_item` into `suggest_outfit` and `create_fit_card`."

**How to test:**
1. Execute `run_agent(query, wardrobe)` 5 times with queries that produce at least one search result.
2. In each run, record the string ID stored in `session['selected_item']['id']`.
3. Inspect the argument passed to `suggest_outfit` to check `new_item['id']`, and inspect the argument passed to `create_fit_card` to check `new_item['id']`.
4. Compare all three values: `session['selected_item']['id'] == suggest_outfit_arg['id'] == create_fit_card_arg['id']`.
5. **Pass condition:** In 5 of 5 runs, all three ID values are identical.

---

### 4. "In at least 4 of 5 successful runs, the generated fit card contains both the listing's price (formatted with a dollar sign) and the platform name, and is between 2 and 4 sentences long."

**How to test:**
1. Take 5 successful agent runs that returned a fit card string in `session['fit_card']`.
2. For each run:
   - Check if the listing price with a dollar sign (e.g., `f"${int(price)}"` or `f"${price:.2f}"`) appears as a substring in `session['fit_card']`.
   - Check if the platform name (e.g., `depop`, `poshmark`, or `thredUp`, case-insensitively) appears as a substring in `session['fit_card']`.
   - Count sentences by splitting on terminal punctuation (`.`, `!`, `?` followed by whitespace or end of string) to confirm the count is within `[2, 4]`.
3. Count how many of the 5 runs satisfy all three checks.
4. **Pass condition:** Count is >= 4 out of 5.

---

### 5. "Given a query specifying a maximum price ceiling, in 5 of 5 runs where an item is found, the price of `session['selected_item']['price']` is less than or equal to the specified price ceiling."

**How to test:**
1. Execute `run_agent(query, wardrobe)` 5 times using queries with explicit price ceilings (e.g., `'vintage graphic tee under $30'`, `'denim jacket under $50'`).
2. For each run that finds an item, extract the numeric price ceiling from the query (`30.0` or `50.0`) and retrieve the float `session['selected_item']['price']`.
3. Evaluate the inequality: `session['selected_item']['price'] <= ceiling`.
4. **Pass condition:** In 5 of 5 runs where an item is found, the inequality holds true.
