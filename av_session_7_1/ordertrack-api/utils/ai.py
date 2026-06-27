"""Minimal LLM client stand-in for the demo AI endpoints.

NOTE (demo): this is a stub — it does NOT call a real model. It exists so the
intentionally-vulnerable /api/reviews/summary endpoint runs end-to-end and the
prompt-injection pattern can be shown without network access or API keys.

A real integration would not look like this. With the Anthropic SDK the call is
``client.messages.create(model=..., messages=[...])`` (there is no
``claude.complete``), and untrusted user text would go in a separate user-role
message — never f-string-concatenated into the instruction.
"""


class _Claude:
    def complete(self, prompt):
        # A real client would send `prompt` to the model and return its reply.
        return f"[demo summary] {prompt}"


claude = _Claude()
