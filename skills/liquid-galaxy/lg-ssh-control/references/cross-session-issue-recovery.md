# Cross-Session Issue Recovery

## Why

LG issues often repeat between sessions — a known bug that was diagnosed in a past session may still be present. When the user says "this was identified in session X" or references a past conversation, use `session_search` to recover the root cause.

## Procedure

1. **User references a past issue** — Use `session_search(query="<keywords>")` to find sessions discussing the topic.
2. **User gives a session ID** — Pass it directly to `session_search(query="<session-id>")` or use browse mode `session_search()` to locate it by date.
3. **Scroll the match** — Use `session_search(session_id="<id>", around_message_id=<match_id>, window=20)` to read the full context around the discovery.
4. **Extract the root cause** — Read diagnostic output, error messages, and the eventual fix from the session.
5. **Apply the fix without re-debugging** — Once you understand what went wrong and why, fix it directly. Don't repeat the investigation.

## Example (June 2026)

User: "lg2 did not turn off. this issue was identified in session id 20260619_093122_24d748"

Agent:
1. `session_search(query="20260619_093122_24d748")` → found the session (210 messages about LG ops)
2. `session_search(query="poweroff")` → found a match in session `20260613_210357_8d5606` where the original `lg-poweroff-direct` helper was written with a self-first bug (powered off lg1 → SSH dropped → lg2 never reached)
3. Read the bookend messages to confirm the exact issue
4. Fixed the deployed helper on lg1 directly (no re-debugging needed)

## When to Use

- User says "this happened before" or "we fixed this in an earlier session"
- User gives a specific session ID
- A known fix exists but you're unsure of the exact details
- Before attempting a new fix that might duplicate past work
- When the user corrects you ("you already know this from session X")
