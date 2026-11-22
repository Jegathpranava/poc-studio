"""Per-million-token prices in USD. Free gateway aliases cost nothing."""

FREE_MODELS: frozenset[str] = frozenset({"fast", "smart", "vision", "embed", "guard"})

# VERIFY_PRICE: first-party Anthropic list prices from the claude-api skill model table
# (cached 2026-11-03). The gateway may bill differently; confirm against the gateway's
# `usage` with the live test (owner-only step) before relying on them.
CLAUDE_HAIKU_5_5_IN_PER_M = 0.10  # VERIFY_PRICE (list price holds for prompts up to 100K tokens)
CLAUDE_HAIKU_5_5_OUT_PER_M = 0.50  # VERIFY_PRICE
CLAUDE_SONNET_5_5_IN_PER_M = 2.00  # VERIFY_PRICE
CLAUDE_SONNET_5_5_OUT_PER_M = 10.00  # VERIFY_PRICE
CLAUDE_OPUS_5_5_IN_PER_M = 4.00  # VERIFY_PRICE
CLAUDE_OPUS_5_5_OUT_PER_M = 20.00  # VERIFY_PRICE

# model -> (input, output) USD per 1M tokens
PRICES: dict[str, tuple[float, float]] = {
    **{m: (0.0, 0.0) for m in FREE_MODELS},
    "claude-haiku-5-5": (CLAUDE_HAIKU_5_5_IN_PER_M, CLAUDE_HAIKU_5_5_OUT_PER_M),
    "claude-sonnet-5-5": (CLAUDE_SONNET_5_5_IN_PER_M, CLAUDE_SONNET_5_5_OUT_PER_M),
    "claude-opus-5-5": (CLAUDE_OPUS_5_5_IN_PER_M, CLAUDE_OPUS_5_5_OUT_PER_M),
}


def is_claude(model: str) -> bool:
    return model.startswith("claude-")


def prices(model: str) -> tuple[float, float]:
    """Return (input, output) price per 1M tokens. Unknown models are an error, never free."""
    try:
        return PRICES[model]
    except KeyError:
        raise ValueError(f"no price known for model {model!r}") from None


def cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    p_in, p_out = prices(model)
    return (tokens_in * p_in + tokens_out * p_out) / 1_000_000
