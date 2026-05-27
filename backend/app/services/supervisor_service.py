"""
AI Supervisor Service

Provides a conversational interface powered by LLM.
Gives the user a natural language way to interact with the system,
ask questions, and get recommendations to run specific agents.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel


def _get_llm() -> Optional[BaseChatModel]:
    """Initialize the configured LLM using LangChain."""
    settings = get_settings()

    provider = (settings.DEFAULT_LLM_PROVIDER or "groq").lower()

    try:
        if provider == "xai" and settings.XAI_API_KEY:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.XAI_MODEL,
                openai_api_key=settings.XAI_API_KEY,
                openai_api_base="https://api.x.ai/v1",
                temperature=0.4,
            )

        elif provider == "groq" and settings.GROQ_API_KEY:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=settings.GROQ_MODEL,
                groq_api_key=settings.GROQ_API_KEY,
                temperature=0.4,
            )

        elif provider == "openai" and settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.4,
            )

        elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=settings.ANTHROPIC_MODEL,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.4,
            )

    except Exception as e:
        print(f"[Supervisor] Failed to initialize LLM ({provider}): {e}")

    return None


SYSTEM_PROMPT = """You are the Funton AI Supervisor — an intelligent assistant for a futon and mattress manufacturing company.

You help the user understand:
- Inventory levels and shortages
- Production capacity and bottlenecks
- Demand, quotes, and sales pipeline
- What the specialized agents (MRP, Inventory Intelligence, Production Scheduler) should focus on

Your personality:
- Professional, concise, and action-oriented
- You speak in the context of real manufacturing operations
- You frequently reference specific data (item codes like FG-002, RM-010, CM-030, work centers like Assembly A, customers like Restoration Hardware)
- When appropriate, you recommend running one of the three agents and explain why

Available agents you can suggest:
1. MRP Agent → material planning and purchase order recommendations
2. Inventory Intelligence Agent → ABC analysis, reorder points, dead stock
3. Production Scheduler Agent → capacity and work center scheduling

Important rules:
- Never claim you executed an action yourself. You only propose and recommend.
- If the user says yes to running an agent, clearly indicate which one.
- Keep responses relatively short and practical.
- Use real-sounding manufacturing context from the Funton operation.
"""


async def chat_with_supervisor(
    db: AsyncSession,
    messages: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Main entry point for the AI Supervisor chat.
    Takes conversation history and returns the next response.
    """
    settings = get_settings()
    llm = _get_llm()

    if not llm:
        provider = (settings.DEFAULT_LLM_PROVIDER or "none").lower()
        key_name = {
            "xai": "XAI_API_KEY",
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }.get(provider, "the correct API key")

        # Helpful debug info
        print(f"[Supervisor] LLM init failed. Provider={provider}, Looking for {key_name}")
        print(f"[Supervisor] XAI_API_KEY present: {bool(settings.XAI_API_KEY)}")
        print(f"[Supervisor] GROQ_API_KEY present: {bool(settings.GROQ_API_KEY)}")
        print(f"[Supervisor] OPENAI_API_KEY present: {bool(settings.OPENAI_API_KEY)}")
        print(f"[Supervisor] ANTHROPIC_API_KEY present: {bool(settings.ANTHROPIC_API_KEY)}")

        return {
            "response": f"The AI Supervisor LLM is not active (provider: {provider}, no valid {key_name} found).\n\n"
                        "→ Go to https://console.x.ai/ to get an XAI_API_KEY\n"
                        "→ Set DEFAULT_LLM_PROVIDER=xai and XAI_API_KEY in backend/.env\n"
                        "→ Restart the backend after editing .env\n\n"
                        "For now, here's a simulated response: The main opportunities right now are hinge shortages and capacity at Assembly A.",
            "suggested_agent": "production_scheduler",
        }

    # Convert frontend messages to LangChain format
    langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for msg in messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["text"]))
        elif msg["role"] == "agent":
            langchain_messages.append(AIMessage(content=msg["text"]))

    try:
        response = await llm.ainvoke(langchain_messages)
        content = response.content.strip()

        # Very lightweight intent detection for suggesting agents
        suggested_agent = None
        lower = content.lower()
        if "production scheduler" in lower or "assembly a" in lower:
            suggested_agent = "production_scheduler"
        elif "mrp" in lower or "purchase" in lower or "material" in lower:
            suggested_agent = "mrp"
        elif "inventory" in lower or "reorder" in lower or "abc" in lower:
            suggested_agent = "inventory"

        return {
            "response": content,
            "suggested_agent": suggested_agent,
        }

    except Exception as e:
        error_str = str(e).lower()

        if "invalid_api_key" in error_str or "401" in error_str or "authentication" in error_str:
            provider = (settings.DEFAULT_LLM_PROVIDER or "openai").lower()
            key_name = {
                "groq": "GROQ_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
            }.get(provider, "the correct API key")

            print(f"[Supervisor] LLM authentication failed for {key_name} — falling back to simulation.")

            # Graceful fallback so the user isn't spammed with errors
            return {
                "response": "I'm currently running in simulation mode (LLM authentication failed). "
                            "The main opportunities right now appear to be capacity at Assembly A and some material shortages. "
                            "Would you like me to run the Production Scheduler or MRP Agent?",
                "suggested_agent": "production_scheduler",
            }

        elif "not_found_error" in error_str or "model" in error_str and "404" in error_str:
            provider = (settings.DEFAULT_LLM_PROVIDER or "openai").lower()
            print(f"[Supervisor] Model not found for provider {provider} — falling back to simulation.")

            return {
                "response": "I'm currently running in simulation mode (model configuration issue). "
                            "The main opportunities right now appear to be capacity at Assembly A and some material shortages. "
                            "Would you like me to run the Production Scheduler or MRP Agent?",
                "suggested_agent": "production_scheduler",
            }

        else:
            print(f"[Supervisor] Unexpected LLM error: {e} — falling back to simulation.")
            return {
                "response": "I'm currently running in simulation mode due to a temporary issue. "
                            "The main opportunities right now appear to be capacity at Assembly A and some material shortages. "
                            "Would you like me to run the Production Scheduler or MRP Agent?",
                "suggested_agent": "production_scheduler",
            }
