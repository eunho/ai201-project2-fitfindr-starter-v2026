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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



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

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
