"""
Single value extraction across providers.

extract(model, text, field, instruction) returns the model's extracted value as
a string. The provider is inferred from the model name:
  claude*  -> Anthropic (tool use)
  gpt* / o* -> OpenAI (function calling)

Set ANTHROPIC_API_KEY and/or OPENAI_API_KEY in the environment (a .env file is
loaded if python-dotenv is installed).
"""

import os
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

_anthropic = None
_openai = None


def _tool_schema(field):
    return {
        "name": "record",
        "description": "Record exactly one short extracted value.",
        "properties": {field: {
            "type": "string",
            "description": "The value only, as few words as possible, not a sentence.",
        }},
    }


def _extract_anthropic(model, text, field, instruction):
    global _anthropic
    if _anthropic is None:
        import anthropic
        _anthropic = anthropic.Anthropic()
    s = _tool_schema(field)
    msg = _anthropic.messages.create(
        model=model, max_tokens=128,
        tools=[{"name": s["name"], "description": s["description"],
                "input_schema": {"type": "object", "properties": s["properties"], "required": [field]}}],
        tool_choice={"type": "tool", "name": "record"},
        messages=[{"role": "user", "content": f"{instruction}\n\nText:\n{text}"}],
    )
    for b in msg.content:
        if b.type == "tool_use":
            return str(b.input.get(field, "")).strip()
    return ""


def _extract_openai(model, text, field, instruction):
    global _openai
    if _openai is None:
        from openai import OpenAI
        _openai = OpenAI()
    s = _tool_schema(field)
    kwargs = dict(
        model=model,
        messages=[{"role": "user", "content": f"{instruction}\n\nText:\n{text}"}],
        tools=[{"type": "function", "function": {
            "name": s["name"], "description": s["description"],
            "parameters": {"type": "object", "properties": s["properties"], "required": [field]}}}],
        tool_choice={"type": "function", "function": {"name": "record"}},
    )
    # reasoning models (gpt-5, o-series) spend tokens on reasoning before the call
    if model.startswith("gpt-5") or model.startswith("o"):
        kwargs["max_completion_tokens"] = 4000
    else:
        kwargs["max_tokens"] = 128
    resp = _openai.chat.completions.create(**kwargs)
    m = resp.choices[0].message
    if m.tool_calls:
        try:
            return str(json.loads(m.tool_calls[0].function.arguments).get(field, "")).strip()
        except Exception:
            return ""
    return ""


def extract(model, text, field, instruction):
    if model.startswith("claude"):
        return _extract_anthropic(model, text, field, instruction)
    if model.startswith("gpt") or model.startswith("o"):
        return _extract_openai(model, text, field, instruction)
    raise ValueError(f"Unknown provider for model '{model}'. Use a claude* or gpt*/o* model.")
