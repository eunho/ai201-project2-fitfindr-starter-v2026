"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re
import config
from generate import generate
from utils.data_loader import load_listings

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "for", "with", "and", "or",
    "to", "of", "under", "size", "looking", "want", "need", "find",
}


def _matches_size(target: str, item_size: str) -> bool:
    """Check if item_size matches target size case-insensitively with boundary safety."""
    if not target or not item_size:
        return False
    t_clean = target.strip().upper()
    i_clean = item_size.strip().upper()
    if t_clean == i_clean:
        return True
    tokens = [tok.strip() for tok in re.split(r"[/()\s,-]+", i_clean) if tok.strip()]
    if t_clean in tokens:
        return True
    target_num = re.sub(r"^(US|W)\s*", "", t_clean)
    token_nums = [re.sub(r"^(US|W)\s*", "", tok) for tok in tokens]
    if target_num and target_num in token_nums:
        return True
    if "ONE SIZE" in t_clean and "ONE SIZE" in i_clean:
        return True
    return False


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    Returns:
        A list of matching listing dicts, best match first (at most config.SEARCH_RESULT_LIMIT).
        Returns an empty list [] when nothing matches.
    """
    listings = load_listings()

    words = re.findall(r"[a-zA-Z0-9]+", (description or "").lower())
    keywords = [w for w in words if w not in STOP_WORDS]
    if not keywords and words:
        keywords = words

    scored = []
    for item in listings:
        if max_price is not None and item["price"] > max_price:
            continue
        if size is not None and not _matches_size(size, item.get("size", "")):
            continue

        score = 0
        if not keywords:
            score = 1
        else:
            title_text = item["title"].lower()
            desc_text = item["description"].lower()
            tags_text = " ".join(item.get("style_tags", [])).lower()
            category_text = item.get("category", "").lower()
            colors_text = " ".join(item.get("colors", [])).lower()
            brand_text = (item.get("brand") or "").lower()

            for kw in keywords:
                if kw in title_text:
                    score += 4
                if kw in tags_text or kw in category_text:
                    score += 3
                if kw in desc_text:
                    score += 2
                if kw in colors_text or kw in brand_text:
                    score += 1

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: (-x[0], x[1]["price"]))
    return [item for _, item in scored[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    Handles empty wardrobes gracefully by returning general styling advice.
    """
    items = wardrobe.get("items", []) if wardrobe else []
    title = new_item.get("title", "thrifted item")
    category = new_item.get("category", "")
    colors = ", ".join(new_item.get("colors", []))
    style_tags = ", ".join(new_item.get("style_tags", []))
    condition = new_item.get("condition", "")
    desc = new_item.get("description", "")

    if not items:
        prompt = (
            f"You are a personal fashion stylist. A shopper found this thrifted item:\n"
            f"- Title: {title}\n"
            f"- Category: {category}\n"
            f"- Colors: {colors}\n"
            f"- Style: {style_tags}\n"
            f"- Condition: {condition}\n"
            f"- Description: {desc}\n\n"
            f"The user has an empty wardrobe saved. Provide 1 to 2 stylish outfit concepts and silhouette pairing ideas "
            f"for this piece using versatile wardrobe essentials (e.g. types of denim, layers, shoes). "
            f"Be concise, creative, and practical."
        )
    else:
        wardrobe_lines = []
        for it in items:
            it_name = it.get("name", "item")
            it_cat = it.get("category", "")
            it_colors = ", ".join(it.get("colors", []))
            it_tags = ", ".join(it.get("style_tags", []))
            it_notes = f" ({it.get('notes')})" if it.get("notes") else ""
            wardrobe_lines.append(f"- {it_name} [{it_cat}, colors: {it_colors}, style: {it_tags}]{it_notes}")
        wardrobe_str = "\n".join(wardrobe_lines)

        prompt = (
            f"You are a personal fashion stylist. A shopper is considering this thrifted find:\n"
            f"- Title: {title}\n"
            f"- Category: {category}\n"
            f"- Colors: {colors}\n"
            f"- Style: {style_tags}\n"
            f"- Condition: {condition}\n"
            f"- Description: {desc}\n\n"
            f"Here are the items currently in their closet:\n"
            f"{wardrobe_str}\n\n"
            f"Suggest 1 or 2 distinct outfit combinations that style this thrifted find with pieces from their closet. "
            f"Explicitly name the specific wardrobe items they already own and briefly explain why the colors and silhouettes work together. "
            f"Keep it concise, direct, and inspiring."
        )

    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    Returns a 2-to-4 sentence caption mentioning the item, price, platform, and vibe.
    """
    price = new_item.get("price", 0)
    price_str = f"${int(price)}" if price == int(price) else f"${price:.2f}"
    platform = new_item.get("platform", "thrift")
    title = new_item.get("title", "thrift find")

    if not outfit or not outfit.strip():
        return (
            f"Just scooped up this {title} on {platform} for {price_str}! "
            f"Such a solid thrift find with immaculate vintage energy. "
            f"Can't wait to get this into rotation."
        )

    style_vibe = ", ".join(new_item.get("style_tags", []))
    prompt = (
        f"Write a social media fit check caption (strictly 2 to 4 sentences) showing off a recent thrift find.\n\n"
        f"Item Details:\n"
        f"- Title: {title}\n"
        f"- Price: {price_str}\n"
        f"- Platform: {platform}\n"
        f"- Style vibe: {style_vibe}\n\n"
        f"Styling Context from Stylist:\n"
        f"{outfit}\n\n"
        f"Requirements:\n"
        f"1. Write in an authentic, natural social media caption voice (like an Instagram or TikTok caption) — NOT a marketing product pitch.\n"
        f"2. Mention the item, its price ({price_str}), and the platform ({platform}) once each.\n"
        f"3. Capture the aesthetic vibe and how it's styled.\n"
        f"4. Length MUST be between 2 and 4 sentences. Do not use hashtags or wrapping quotation marks."
    )

    return generate(prompt)

