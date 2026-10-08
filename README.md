# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

A user provides a natural language query describing a thrift fashion item they are looking for, optionally including size constraints and a maximum price (e.g., 'vintage graphic tee under $30, size M'), along with their current wardrobe. FitFindr parses the request, searches secondhand listings across thrift platforms, and selects the top matching piece. It then generates personalized outfit combinations styling the thrifted find with pieces from the user's existing closet, and writes an engaging, social-ready fit card caption highlighting the find, platform, price, and aesthetic. If no matching items are found, the agent stops early and advises the user on what parameters to adjust.



---

## Tool Inventory

### `search_listings`

- **What it does:** Searches thrift catalog listings filtered by optional size and price ceiling, ranking matching items by keyword overlap with the description.
- **Inputs:** `description` (str) — search keywords describing desired piece; `size` (str | None) — size filter matched case-insensitively with boundary/token safety (e.g. 'M' matches 'M' or 'S/M', not 'US 9' or 'XL'), or None to skip; `max_price` (float | None) — inclusive price ceiling, or None to skip.
- **Returns:** A list of at most 10 matching listing dicts sorted by keyword relevance descending, where each dict has `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str | None), and `platform` (str).
- **When it has nothing:** An empty list `[]` (not `None`, and does not raise an exception).

### `suggest_outfit`

- **What it does:** Generates 1–2 outfit ideas styling the thrifted find either with compatible pieces from the user's wardrobe or with general styling advice if no wardrobe is provided.
- **Inputs:** `new_item` (dict) — a listing dict for the thrifted item with `title`, `category`, `style_tags`, `colors`, etc.; `wardrobe` (dict) — a wardrobe dict containing an `'items'` key holding a list of wardrobe item dicts (`id`, `name`, `category`, `colors`, `style_tags`, `notes`).
- **Returns:** A non-empty string (`str`) describing 1–2 complete outfit combinations that explicitly name pieces from the user's wardrobe and explain why they work together.
- **When it has nothing:** A non-empty string (`str`) containing general styling ideas, silhouette pairings, and aesthetic advice for `new_item` when `wardrobe['items']` is empty (never returns `""` and never raises an exception).

### `create_fit_card`

- **What it does:** Generates a short, engaging 2–4 sentence social-media-ready caption highlighting the find, styling vibe, price, and platform.
- **Inputs:** `outfit` (str) — outfit suggestion text from `suggest_outfit`; `new_item` (dict) — listing dict containing `title`, `price` (float), `platform` (str), `category`, and style details.
- **Returns:** A 2–4 sentence caption string (`str`) written in an authentic social posting tone mentioning the item, its price, its platform, and the outfit vibe.
- **When it has nothing:** A fallback caption string (`str`) describing the item, platform, and price directly when `outfit` is empty or whitespace-only (never returns `""` and never raises an exception).

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list `[]`, put an actionable message in `session["error"]` explaining what criteria the user could adjust (such as raising the price ceiling or broadening search terms) and stop the loop immediately without calling `suggest_outfit` or `create_fit_card`. Otherwise, select the first result (`session["search_results"][0]`), store it in `session["selected_item"]`, and proceed to call `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regular expressions (regex) and token parsing to extract price ceilings (e.g. `under $30`, `<$30`), size specifications (e.g. `size M`, `size 8`), and clean the remaining tokens as the item description.

**What moves through the session:**
1. `session["query"]` (str) and `session["wardrobe"]` (dict) initialized at loop start.
2. `session["parsed"]` (dict: `description`, `size`, `max_price`) populated by query parser.
3. `session["search_results"]` (list[dict]) populated by `search_listings`.
4. Branch: if empty, set `session["error"]` (str) and return session; if non-empty, set `session["selected_item"]` (dict).
5. `session["outfit_suggestion"]` (str) populated by `suggest_outfit(selected_item, wardrobe)`.
6. `session["fit_card"]` (str) populated by `create_fit_card(outfit_suggestion, selected_item)`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Graphic Tee — 2003 Tour Bootleg Style — $24.0 on depop

  Outfit:   Hey! As your stylist, I give this graphic tee a resounding **yes**. It has that effortless, lived-in energy that instantly elevates a casual outfit. 

Here are 2 distinct ways to style it using pieces already in your closet:

### Look 1: 90s Streetwear Edge
* **The Outfit:** Pair the graphic tee with your **baggy straight-leg jeans (dark wash)**, layered under the **vintage black denim jacket**, and finished with your **chunky white sneakers** and **black crossbody bag**. 
* **Why it works:** This is all about playing with proportion and texture. The slightly boxy fit of the tee tucks seamlessly into the high-waisted, baggy dark-wash denim for that classic 90s skater silhouette. Adding the cropped black denim jacket creates a cool monochromatic top layer that contrasts with the indigo jeans, while the chunky white sneakers break up the dark tones and tie the streetwear aesthetic together.

### Look 2: Grunge-Infused Contrast
* **The Outfit:** Tuck the graphic tee into your **wide-leg khaki trousers**, cinched with the **brown leather belt**, and style it with your **black combat boots** and **black crossbody bag**. 
* **Why it works:** This outfit leans into high-low styling by mixing grungy elements with tailored streetwear. The faded black tee and rugged combat boots bring a dark, edgy attitude that grounds the lighter, earthy khaki trousers. Using the brown leather belt adds a rich accent color that bridges the gap between the khaki pants and black accessories, while the wide-leg silhouette creates an effortlessly cool, balanced shape against the boxy top.

  Fit card: Scored this unreal 2003 tour bootleg graphic tee on depop for just $24, and it instantly brings that effortless grunge energy to my closet. I love styling it with baggy dark denim and a black jacket for 90s streetwear vibes, or contrasting it with khaki trousers and combat boots. It’s got that perfect lived-in feel that makes throwing together an outfit way too easy.
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Here are two distinct ways to style your new vintage Levi’s 501s using pieces already in your closet:

### Look 1: Effortless Streetwear (Casual & Cool)
* **Pair with:** White ribbed tank top, oversized grey crewneck sweatshirt, chunky white sneakers, and black crossbody bag.
* **Why it works:** The straight-leg silhouette of the 501s balances out the extreme volume of the oversized grey crewneck, creating that effortless high-low streetwear proportion. Tucking in the white tank (or letting the hem peek out) breaks up the grey and blue tones, while the chunky white sneakers tie the crisp white top and casual vibe together.

### Look 2: Grunge-Chic Edge (Tough & Tailored)
* **Pair with:** Black cropped zip hoodie, vintage black denim jacket, black combat boots, and brown leather belt.
* **Why it works:** Pairing medium-wash blue denim with black outerwear creates a sharp, high-contrast look. The cropped proportions of both the hoodie and the black denim jacket sit right at the waist, accentuating the high-rise fit of the 501s. Grounding the outfit with black combat boots adds a tough, grunge-inspired edge, while the brown belt adds a subtle, warm vintage contrast.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Scored these vintage Levi's 501 jeans on depop for just $38 and I am never taking them off. The medium wash has that perfectly worn-in look that makes any basic streetwear fit instantly cool. Just threw them on with my favorite white sneakers for a casual, classic vibe.
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked the AI to write a size-filtering helper function for `search_listings` that determines if a requested user size matches the listing's size string.
- *What came back:* The AI initially suggested a direct substring membership test: `target_size.lower() in item["size"].lower()`.
- *What I changed:* I noticed this naive substring check produces critical false positives (e.g. searching for size `'s'` matches `'us 9'` shoes, and searching for `'l'` matches `'xl'` oversized items). I changed the implementation to tokenize listing size strings across delimiters (`/`, `()`, `-`), normalize prefix abbreviations (`US`, `W`), and require exact token equality in `_matches_size()`.

**Moment 2**

- *What I asked for:* I asked the AI to design the generation prompt for `create_fit_card` to craft social-ready captions from the item data and styling output.
- *What came back:* The AI generated a broad marketing prompt that produced promotional brand ad copy ("Introducing the iconic Levi 501s...") cluttered with hashtags (`#vintage #ootd`) and wrapped in quotation marks.
- *What I changed:* I revised the prompt with strict structural rules: explicitly ban hashtags and quotation marks, mandate an authentic personal social posting voice (like an Instagram or TikTok fit check), require mentioning the platform and exact price formatted with a dollar sign, and restrict length strictly to between 2 and 4 sentences so it consistently meets our acceptance criteria.

**Moment 3 (Unit 4)**

- *What I asked for:* In Unit 4, I asked the AI to critique our failure messages from an end-user perspective and suggest prompt constraints to prevent repetitive fit card openings.
- *What came back:* The AI identified that the model was defaulting to identical opening templates (*"Scored this..."*) across every run, and recommended negative prompting combined with grounding rules.
- *What I changed:* Rather than hardcoding string templates, I added negative constraints prohibiting formulaic openings (*"do NOT start with formulaic openings like 'Scored this...' or 'Found this...'"*) and mandated referencing specific closet pieces from `outfit_suggestion`. This preserved natural conversational variety while ensuring verifiable wardrobe synthesis.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Session state preserves selected item across tool calls | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card includes price, platform, and proper length | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search strictly respects price ceilings | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
=== Criterion 1: matching query completes all three tools (Try 1) ===
File: agent.py :: Function: run_agent
Query: 'vintage graphic tee under $30'

Selected item: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
Search results: 10 items

Outfit suggestion:
Here are two distinct ways to style your new graphic tee using pieces already in your closet:

### 1. The 90s Streetwear Slouch
* **Items to pair:** Baggy straight-leg jeans (dark wash) + Chunky white sneakers + Black crossbody bag
* **Why it works:** The slightly boxy fit of the tee mirrors the relaxed volume of the baggy jeans, nailing an effortless, skater-inspired streetwear silhouette. The faded black top and dark indigo wash create a moody, cohesive base, while the chunky white sneakers break up the darkness and tie into the vintage graphic's lighter tones.

### 2. Grunge-Utility Contrast
* **Items to pair:** Wide-leg khaki trousers + Black combat boots + Vintage black denim jacket (layered over top) + Brown leather belt
* **Why it works:** This look plays on high-low contrasts by pairing the edgy, worn-in band tee with clean, earthy wide-leg trousers. Tucking the tee in (cinched with the brown belt) defines your waist against the voluminous pants, while the cropped black denim jacket and combat boots anchor the outfit in heavy grunge textures.

Fit card:
Scored this sick 2003 tour bootleg graphic tee on Depop for just $24, and it instantly became my favorite piece. I'm leaning into total grunge streetwear today by pairing the faded vintage cut with baggy dark wash jeans and chunky sneakers. Thrift magic is real.


=== Criterion 2: impossible query stops before second tool (Try 1) ===
File: agent.py :: Function: run_agent (via _format_no_results_message)
Query: 'designer ballgown size XXS under $5'

stopped early: yes — No thrift listings matched 'designer ballgown'. Try raising your price ceiling above $5, checking adjacent sizes instead of 'XXS' or using broader keywords (e.g. searching for 'jacket' or 'tee' instead of specific styles).
selected_item: (none)
search_results: 0

Trace:
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    empty, stopping


=== Criterion 3: session preserves selected item across calls (Try 1) ===
File: agent.py :: Function: run_agent
Query: 'denim jacket under $50'

selected_item['id']: 'lst_007' ('Denim Jacket — Light Wash, Cropped', $42.0, poshmark)
suggest_outfit argument new_item['id']: 'lst_007'
create_fit_card argument new_item['id']: 'lst_007'

Trace:
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 7 items: Denim Jacket — Light Wash, Cropped, High-Waisted Denim Shorts — Cutoff, Denim Vest — Medium Wash, Studded … +4 more
[2] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Here are two distinct, effortlessly cool ways to style your new light wash cropped denim jacket using pieces s…
[3] create_fit_card
      in:  dict with keys: item, price, platform
      out: Found this light wash cropped denim jacket on Poshmark for just $42 and honestly, it's the ultimate streetwear…


=== Criterion 4: fit card includes price, platform, and proper length (Try 1) ===
File: tools.py :: Function: create_fit_card
Query: 'silk slip dress in midi length under $40'

Fit card:
Scored this gorgeous 90s floral silk slip dress on depop for just $30 and I am completely obsessed. I’ve been styling it with chunky combat boots and an oversized crewneck for that perfect grunge-chic look, but it’s just as cute layered over a baby tee with sneakers. It’s giving the ultimate vintage cottagecore meets streetwear energy.

Verification:
- Price: '$30' present
- Platform: 'depop' present
- Sentence count: 3 sentences (meets 2-4 sentence requirement)


=== Criterion 5: search strictly respects price ceilings (Try 1) ===
File: tools.py :: Function: search_listings (via MCP)
Query: 'vintage graphic tee under $25'

Price ceiling: $25.0
Selected item: 'Graphic Tee — 2003 Tour Bootleg Style'
Selected item price: $24.0 (satisfies price <= 25.0)
All 10 search results returned had prices <= $25.0:
- lst_006: $24.0
- lst_033: $19.0
- lst_002: $18.0
- lst_012: $20.0
- lst_017: $15.0
- lst_027: $22.0
- lst_022: $18.0
- lst_030: $16.0
- lst_025: $14.0
- lst_035: $22.0
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | MET | All 5 tries completed `search_listings (via MCP)`, `suggest_outfit`, and `create_fit_card`, returning non-empty fit card captions (5/5 exceeds 4/5 target). |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET | In all 5 tries, the empty search result triggered the branch to halt before `suggest_outfit` and set an actionable adjustment message in `session['error']` (5/5 meets 5/5 target). |
| 3 | Session state preserves selected item across tool calls | 5 of 5 | MET | In all 5 tries, `session['selected_item']['id']` held `'lst_007'`, matching exactly the `new_item['id']` provided to `suggest_outfit` and `create_fit_card` (5/5 meets 5/5 target). |
| 4 | Fit card includes price, platform, and proper length | 4 of 5 | MET | All 5 tries contained the dollar price (`$30`), platform (`depop`/`Depop`), and had exactly 3 sentences within the required 2–4 sentence range (5/5 exceeds 4/5 target). |
| 5 | Search strictly respects price ceilings | 5 of 5 | MET | For a query specifying a $25 ceiling, all 5 tries selected item `lst_006` ($24.0), and all 10 items returned across every try were <= $25.0 (5/5 meets 5/5 target). |

**Diagnoses**

- **Pattern Analysis**: No criteria were missed across the 25 evaluation runs (all 5 criteria achieved 5/5 passes).
  - Criteria 2, 3, and 5 evaluate deterministic Python logic (early-stopping conditional branch, in-memory session dictionary propagation, and mathematical inequality filtering `item['price'] <= max_price`). Because these execution paths involve no stochastic model decisions, 5 of 5 reliability was sustained.
  - Criteria 1 and 4 involve generative model calls via Gemini 3.5 Flash Lite (`suggest_outfit` and `create_fit_card`). Both passed 5 of 5 times despite a relaxed target of 4 of 5. The pacing and retry logic in `generate.py` prevented transient API throttling from failing runs, and the structured constraints in `create_fit_card`'s prompt reliably forced the model to include dollar-formatted prices, platform names, and stay within the 2–4 sentence boundary.

- **Honest Target Assessment**:
  - The target of 4 of 5 for **Criterion 1** was set conservatively to buffer against network drops or rate-limit timeouts. In practice, `generate.py`'s automatic backoff makes completion 100% reliable, so Criterion 1 could fairly be set to 5 of 5.
  - **Criterion 4** ("fit card includes price, platform, and proper length") had too lenient a target and scope. While requiring price, platform, and 2–4 sentences tested basic formatting compliance, it did not test whether the fit card actually synthesized wardrobe context from `outfit_suggestion`. The model was able to satisfy the criterion with generic styling phrasing without referencing specific closet pieces.

- **Criterion to Tighten**:
  - I would tighten **Criterion 4** to evaluate wardrobe grounding and variety: *"In at least 4 of 5 tries across different items, the fit card explicitly names at least one specific wardrobe item passed from the user's closet in `outfit_suggestion` and shares no opening sentence with prior cards."* This would test whether the model is truly contextualizing closet pieces rather than relying on formulaic opening sentences like *"Scored this [adjective] [title] on [platform] for just $[price]..."*.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey, Vintage Graphic Hoodie — Faded Black … +7 more
[2] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Hey! As your stylist, I give this graphic tee a resounding **yes**. It has that effortless, lived-in energy th…
[3] create_fit_card
      in:  dict with keys: item, price, platform
      out: Scored this unreal 2003 tour bootleg graphic tee on depop for just $24, and it instantly brings that effortles…

  Found:    Graphic Tee — 2003 Tour Bootleg Style — $24.0 on depop

  Outfit:   Hey! As your stylist, I give this graphic tee a resounding **yes**. It has that effortless, lived-in energy that instantly elevates a casual outfit. 

Here are 2 distinct ways to style it using pieces already in your closet:

### Look 1: 90s Streetwear Edge
* **The Outfit:** Pair the graphic tee with your **baggy straight-leg jeans (dark wash)**, layered under the **vintage black denim jacket**, and finished with your **chunky white sneakers** and **black crossbody bag**. 
* **Why it works:** This is all about playing with proportion and texture. The slightly boxy fit of the tee tucks seamlessly into the high-waisted, baggy dark-wash denim for that classic 90s skater silhouette. Adding the cropped black denim jacket creates a cool monochromatic top layer that contrasts with the indigo jeans, while the chunky white sneakers break up the dark tones and tie the streetwear aesthetic together.

### Look 2: Grunge-Infused Contrast
* **The Outfit:** Tuck the graphic tee into your **wide-leg khaki trousers**, cinched with the **brown leather belt**, and style it with your **black combat boots** and **black crossbody bag**. 
* **Why it works:** This outfit leans into high-low styling by mixing grungy elements with tailored streetwear. The faded black tee and rugged combat boots bring a dark, edgy attitude that grounds the lighter, earthy khaki trousers. Using the brown leather belt adds a rich accent color that bridges the gap between the khaki pants and black accessories, while the wide-leg silhouette creates an effortlessly cool, balanced shape against the boxy top.

  Fit card: Scored this unreal 2003 tour bootleg graphic tee on depop for just $24, and it instantly brings that effortless grunge energy to my closet. I love styling it with baggy dark denim and a black jacket for 90s streetwear vibes, or contrasting it with khaki trousers and combat boots. It’s got that perfect lived-in feel that makes throwing together an outfit way too easy.
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    empty, stopping

  No thrift listings matched 'designer ballgown'. Try raising your price ceiling above $5, checking adjacent sizes instead of 'XXS' or using broader keywords (e.g. searching for 'jacket' or 'tee' instead of specific styles).
```

**On the MCP move:**
Moved `search_listings` onto FastMCP in `mcp_server.py`, exposing typed parameters `description: str`, `size: str | None = None`, and `max_price: float | None = None`. In `agent.py`, the direct function call was replaced with `mcp_client.call_tool("search_listings", {...})`. The return value remained identical in schema and content (`list[dict]`), so all downstream planning logic and prompt construction functioned without changes.



---

## The Improvement

**What I changed:**
In `tools.py::create_fit_card`, revised the LLM prompt instructions: explicitly mandated that the fit card name at least one specific wardrobe piece from the closet mentioned in the stylist's context to ground the outfit, and instructed the model to vary its syntax and avoid repetitive, cliché openings like *"Scored this..."* or *"Found this..."*.

**Which failure it was meant to fix:**
Addressed the diagnostic weakness identified in Milestone 4 for Criterion 4: previous fit cards relied on formulaic, templated opening sentences (*"Scored this [adjective] [title] on [platform] for just $[price]..."*) and produced generic praise rather than synthesizing the specific wardrobe pieces recommended in `outfit_suggestion`.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Session state preserves selected item across tool calls | 5 of 5 | PASS | PASS | FAIL | FAIL | PASS | MISSED (3/5) |
| 4. Fit card includes price, platform, and proper length | 4 of 5 | PASS | PASS | PASS | PASS | FAIL | MET (4/5) |
| 5. Search strictly respects price ceilings | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**
Yes, it significantly improved caption variety and wardrobe grounding:
1. **Opening Hook Diversity**: In the *before* run, 100% of tries opened with *"Scored this..."* or *"Found this..."*. In the *after* run, opening sentences varied across creative hooks: *"Scrolling on depop late at night finally paid off..."*, *"My Poshmark cart finally checked out..."*, *"Depop strikes again with..."*, and *"Bagged this unreal 2003 tour bootleg style graphic tee..."*.
2. **Closet Grounding**: Every generated caption in the *after* run explicitly integrated real closet items from the user's wardrobe (`chunky white sneakers`, `wide-leg khaki trousers`, `oversized grey crewneck sweatshirt`, `baggy straight-leg jeans`).
3. **Tradeoffs and Upstream Reality**: On Criterion 4, Try 5 wrote *"thirty bucks"* instead of formatted *"$30"*, passing 4 of 5 (meeting the 4 of 5 target). On Criterion 3, Tries 3 and 4 were interrupted by an upstream `503 UNAVAILABLE` high-demand spike from the Gemini service during live un-cached testing; our agent's `ModelUnavailable` handler caught this cleanly and halted early without crashing, transparently surfacing the 3/5 result.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

- **Criterion 3: Upstream model availability during un-cached evaluation (Missed 3/5 vs. Target 5/5)**
  - *What broke:* In the un-cached post-improvement evaluation run (`run_eval.py --label after`), Tries 3 and 4 were cut short when the Google Gemini service returned an upstream `503 UNAVAILABLE` spike (*"This model is currently experiencing high demand"*). The agent's error handling caught the exception cleanly and stopped without crashing, but because the session halted before `create_fit_card`, the selected item could not be passed through all three tools on those two tries.
  - *What I'd do:* Update `generate.py` with expanded retry policies specifically tailored for HTTP 503 / high-demand surges (e.g., randomized exponential jitter, higher retry thresholds, or automatic graceful fallback to a secondary lightweight model).
  - *Why I stopped here:* Unit 4 strictly enforces making only one single improvement between the before and after runs. My improvement was intentionally focused on prompt grounding and opening variety in `tools.py::create_fit_card`. Changing network retry logic in `generate.py` would represent a second architectural change, muddying the measurement.

- **Criterion 4: Informal price tokenization edge cases (Met 4/5 vs. Target 4/5)**
  - *What broke:* On Try 5 of the after run, the model wrote *"thirty bucks"* rather than the explicitly required dollar sign token (*"$30"*).
  - *What I'd do:* Add a lightweight deterministic post-processing step in `create_fit_card` that scans the output for `f"${int(price)}"` or `f"${price:.2f}"` and injects the formatted price if the model used slang words.
  - *Why I stopped here:* The prompt adjustment successfully met our target of 4 of 5 passes while completely solving the severe problem of repetitive *"Scored this..."* clichés and missing wardrobe pieces. Adding extra post-processing code would be an unnecessary second modification.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [x] criteria.md has five numbered criteria, each with a target
       [x] Each criterion has a reason underneath it
       [x] All five unit 3 sections above have real content
       [x] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [x] Planning Loop names the branch rule and agent.py::run_agent
       [x] Sample Run: one full query plus the three per-tool tests, as text
       [x] At least four new commits
       [x] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [x] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [x] Run Log — Before, five criteria, five tries each
       [x] Real output pasted underneath, naming file and function
       [x] A verdict on every criterion
       [x] A diagnosis for every miss, naming a place AND a mechanism
       [x] Loop Trace, with the MCP call visible in it
       [x] All three failure modes triggered and handled
       [x] One improvement, with Run Log — After in the same format
       [x] What's Still Broken
       [x] At least four new commits
       [x] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
