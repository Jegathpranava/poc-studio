"""LLM client: gateway or mock provider, JSON repair, pre-call budget guard."""

from poc_studio.llm.budget import BudgetExceeded, InputTooLarge, RunBudget
from poc_studio.llm.client import Result, SchemaError, complete_json, wrap_untrusted
from poc_studio.llm.provider import ChatProvider, ChatReply, get_provider

__all__ = [
    "BudgetExceeded",
    "ChatProvider",
    "ChatReply",
    "InputTooLarge",
    "Result",
    "RunBudget",
    "SchemaError",
    "complete_json",
    "get_provider",
    "wrap_untrusted",
]
