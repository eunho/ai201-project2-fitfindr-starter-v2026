# Milestone 5 — Planning Loop & Branching Analysis

## Branch Rule (One Sentence)

If `search_listings` returns an empty list `[]`, the agent writes an actionable message into `session["error"]` specifying concrete adjustments (such as raising the price ceiling, checking adjacent sizes, or broadening search terms) and halts immediately without invoking downstream tools; otherwise, it assigns `session["selected_item"] = session["search_results"][0]` and proceeds to `suggest_outfit`.

---

## Empty Search Message

```
No thrift listings matched 'designer ballgown'. Try raising your price ceiling above $5, checking adjacent sizes instead of 'XXS' or using broader keywords (e.g. searching for 'jacket' or 'tee' instead of specific styles).
```

---

## Question & Honest Assessment

> **Prompt:** "Here is the message an app shows me when my search returns nothing. I know nothing about how the app works. Tell me what I would try next after reading it. If the honest answer is that I'd have no idea what to try, say that. Don't rewrite the message for me."

### What I Would Try Next After Reading It:

After reading this message, I would know exactly what to do next without needing to understand how the app works behind the scenes:

1. **Raise the price limit**: I would increase the price ceiling above $5 (for example, trying `under $30` or `under $50`), recognizing that $5 is likely too low for this catalog.
2. **Loosen the size requirement**: I would drop the strict `'XXS'` filter or try an adjacent size like `'XS'` or `'S'` to see if similar pieces exist.
3. **Broaden the search terms**: I would replace niche wording like `'designer ballgown'` with broader category terms such as `'dress'`, `'formal gown'`, or `'evening dress'`.
