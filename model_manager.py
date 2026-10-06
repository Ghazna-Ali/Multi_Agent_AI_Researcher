import os

from crewai import LLM


MODEL_OPTIONS = {
    "GPT OSS 120B": "openai/gpt-oss-120b",
    "GPT OSS 20B": "openai/gpt-oss-20b",
    "Qwen 3.8 27B": "qwen/qwen3.8-27b",
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
}

DEFAULT_MODEL = "GPT OSS 120B"


def get_api_key():
    """
    Read GROQ_API_KEY from Streamlit secrets first,
    then fall back to environment variables.
    """

    try:
        import streamlit as st

        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


def create_llm(model_name: str):
    """
    Create a CrewAI LLM using Groq's OpenAI-compatible endpoint.
    """

    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to Streamlit Secrets."
        )

    model_id = MODEL_OPTIONS.get(model_name, MODEL_OPTIONS[DEFAULT_MODEL])

    return LLM(
        model=model_id,
        custom_openai=True,
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        temperature=0.2,
        max_tokens=6000,
    )


def model_id(model_name: str):
    return MODEL_OPTIONS.get(model_name, MODEL_OPTIONS[DEFAULT_MODEL])
