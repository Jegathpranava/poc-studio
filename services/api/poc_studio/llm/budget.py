"""Per-run budget with a pre-call estimate guard."""

from dataclasses import dataclass

import tiktoken

from poc_studio.llm.pricing import cost_usd, is_claude, prices

HAIKU_INPUT_CAP_TOKENS = 12_000

_encoder: tiktoken.Encoding | None = None


class BudgetExceeded(Exception):
    def __init__(self, needed_usd: float, remaining_usd: float) -> None:
        super().__init__(f"needs ${needed_usd:.6f}, only ${remaining_usd:.6f} left in the run budget")
        self.needed_usd = needed_usd
        self.remaining_usd = remaining_usd


class InputTooLarge(Exception):
    def __init__(self, tokens: int, cap: int) -> None:
        super().__init__(f"input is {tokens} tokens, cap is {cap} for paid models")
        self.tokens = tokens
        self.cap = cap


def count_tokens(text: str) -> int:
    global _encoder
    if _encoder is None:
        _encoder = tiktoken.get_encoding("o200k_base")
    return len(_encoder.encode(text, disallowed_special=()))


@dataclass
class RunBudget:
    run_id: str
    limit_usd: float
    spent_usd: float = 0.0

    @property
    def remaining(self) -> float:
        return max(self.limit_usd - self.spent_usd, 0.0)

    def estimate(self, model: str, input_text: str, max_tokens: int) -> float:
        """Input tokens x input price plus max_tokens x output price. Raises InputTooLarge."""
        prices(model)  # unknown model fails early
        tokens = count_tokens(input_text)
        if is_claude(model) and tokens > HAIKU_INPUT_CAP_TOKENS:
            raise InputTooLarge(tokens, HAIKU_INPUT_CAP_TOKENS)
        return cost_usd(model, tokens, max_tokens)

    def check(self, model: str, input_text: str, max_tokens: int) -> float:
        """Estimate and raise BudgetExceeded when it does not fit. Returns the estimate."""
        needed = self.estimate(model, input_text, max_tokens)
        if needed > self.remaining + 1e-12:
            raise BudgetExceeded(needed, self.remaining)
        return needed

    def charge(self, cost: float) -> None:
        self.spent_usd += cost
