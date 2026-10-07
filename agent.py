"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import config
import trace
from mcp_client import call_tool
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


import re


def parse_query(query: str) -> dict:
    """Extract description, size, and max_price from the user query."""
    text = (query or "").strip()
    max_price = None
    size = None

    # 1. Price extraction
    price_match = re.search(
        r"(?:under|<|below|less than|max(?:imum)?\s*(?:price)?)\s*\$?(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if not price_match:
        price_match = re.search(r"\$(\d+(?:\.\d+)?)", text)
    if price_match:
        max_price = float(price_match.group(1))
        text = text[:price_match.start()] + " " + text[price_match.end():]

    # 2. Size extraction
    size_match = re.search(
        r"(?:in\s+)?size\s+([A-Za-z0-9/]+(?:\s+[\d.]+)?(?:\s*\([^)]*\))?)",
        text,
        re.IGNORECASE,
    )
    if not size_match:
        size_match = re.search(r"\b(W\d{2}(?:\s*L\d{2})?)\b", text, re.IGNORECASE)
    if size_match:
        size = size_match.group(1).strip()
        text = text[:size_match.start()] + " " + text[size_match.end():]

    # 3. Clean description
    clean_desc = re.sub(
        r"^(?:looking for a|looking for|find me a|find a|i want a|i need a)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    clean_desc = re.sub(r"[,;]+", " ", clean_desc)
    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()

    return {
        "description": clean_desc,
        "size": size,
        "max_price": max_price,
    }


def _format_no_results_message(parsed: dict) -> str:
    """Build an actionable message explaining what parameters the user could change."""
    suggestions = []
    if parsed.get("max_price") is not None:
        suggestions.append(f"raising your price ceiling above ${parsed['max_price']:g}")
    if parsed.get("size"):
        suggestions.append(f"checking adjacent sizes instead of '{parsed['size']}'")
    suggestions.append("using broader keywords (e.g. searching for 'jacket' or 'tee' instead of specific styles)")

    suggestions_str = (
        " or ".join([", ".join(suggestions[:-1]), suggestions[-1]])
        if len(suggestions) > 1
        else suggestions[0]
    )
    item_desc = parsed.get("description") or "your search"
    return f"No thrift listings matched '{item_desc}'. Try {suggestions_str}."


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. Check session["error"] first — if it isn't None,
        the run ended early and the later fields will still be None.
    """
    session = new_session(query, wardrobe)
    iteration = 1
    trace.check_iterations(iteration)
    trace.start_trace()

    # 1. Parse query
    parsed = parse_query(session["query"])
    session["parsed"] = parsed

    # 2. Search listings using MCP tool call
    try:
        results = call_tool(
            "search_listings",
            {
                "description": session["parsed"].get("description", ""),
                "size": session["parsed"].get("size"),
                "max_price": session["parsed"].get("max_price"),
            },
        )
    except Exception as e:
        session["error"] = (
            f"Search service unavailable: {e}. Please ensure the MCP search server is reachable and try again."
        )
        trace.step(
            "search_listings (via MCP)",
            inputs=session["parsed"],
            returned=None,
            note=f"failed: {e}",
        )
        return session

    session["search_results"] = results
    trace.step(
        "search_listings (via MCP)",
        inputs=session["parsed"],
        returned=results,
        note="empty, stopping" if not results else "",
    )

    # 3. Branch: halt if no results found
    if not session["search_results"]:
        session["error"] = _format_no_results_message(session["parsed"])
        return session

    # 4. State: Select best match
    session["selected_item"] = session["search_results"][0]

    # 5. Suggest outfit based on selected item and wardrobe
    try:
        outfit = suggest_outfit(
            new_item=session["selected_item"],
            wardrobe=session["wardrobe"],
        )
        session["outfit_suggestion"] = outfit
        trace.step(
            "suggest_outfit",
            inputs={
                "item": session["selected_item"].get("title"),
                "wardrobe_items": len(session["wardrobe"].get("items", [])),
            },
            returned=outfit,
        )

        # 6. Create fit card caption
        fit_card = create_fit_card(
            outfit=session["outfit_suggestion"],
            new_item=session["selected_item"],
        )
        session["fit_card"] = fit_card
        trace.step(
            "create_fit_card",
            inputs={
                "item": session["selected_item"].get("title"),
                "price": session["selected_item"].get("price"),
                "platform": session["selected_item"].get("platform"),
            },
            returned=fit_card,
        )
    except ModelUnavailable as e:
        session["error"] = f"Model unavailable: {e}"
        trace.step("model_call", inputs=None, returned=None, note=f"Model unavailable: {e}")
    except Exception as e:
        session["error"] = f"Styling service error: {e}. Try rephrasing your search or running again."
        trace.step("model_call", inputs=None, returned=None, note=f"Error: {e}")

    return session



# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
