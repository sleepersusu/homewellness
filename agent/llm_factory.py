"""LLM factory — maps model name to LangChain LLM instance."""

from langchain_core.language_models import BaseChatModel

OPENAI_MODELS = {
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-5",
    "gpt-5.4-mini",
}

GEMINI_MODELS = {
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-3.1-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3.5-flash",
}

# Displayed in Streamlit selectbox
AVAILABLE_MODELS: list[str] = [
    # OpenAI
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini",
    "gpt-4.1",
    "gpt-5.4-mini",
    "gpt-5",
    # Google Gemini
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3.1-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3.5-flash",
]


def get_llm(model_name: str, temperature: float = 0) -> BaseChatModel:
    """Return a LangChain chat model instance for the given model name."""
    if model_name in OPENAI_MODELS:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name, temperature=temperature)
    if model_name in GEMINI_MODELS:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
    raise ValueError(f"未知模型：{model_name}。支援：{AVAILABLE_MODELS}")
