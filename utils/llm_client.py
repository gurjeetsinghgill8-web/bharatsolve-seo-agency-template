"""
BHARATSOLVE SEO AGENCY — LLM Client
Multi-provider LLM client with fallback chain support.
Supports: Groq, Gemini, OpenAI, DeepSeek, Claude
Uses: Streamlit secrets → encrypted vault → .env → environment
"""
import os
import json
import time
import re
from typing import Optional

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

FALLBACK_CHAIN = CONFIG.get("models", {}).get("fallback_chain", [])

# ── Helper: Get API key with multi-source approach ──

VAULT = None  # Lazy-loaded vault
_STREAMLIT_SECRETS_CHECKED = False

def _check_streamlit_secrets():
    """Check if running on Streamlit Cloud with secrets."""
    global _STREAMLIT_SECRETS_CHECKED
    if _STREAMLIT_SECRETS_CHECKED:
        return
    _STREAMLIT_SECRETS_CHECKED = True
    try:
        import streamlit as st
        # Just attempt to access secrets to trigger the check
        if hasattr(st, 'secrets'):
            pass
    except:
        pass

def _get_vault():
    """Load vault once and cache it."""
    global VAULT
    if VAULT is None:
        try:
            from secure_vault import load_api_keys
            VAULT = load_api_keys()
        except:
            VAULT = {}
    return VAULT

def get_api_key(provider: str) -> Optional[str]:
    """Get API key: Streamlit secrets → vault → .env → environment."""
    env_var_map = {
        "groq": "GROQ_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "claude": "CLAUDE_API_KEY",
    }
    env_var = env_var_map.get(provider, f"{provider.upper()}_API_KEY")
    
    # 1️⃣ Try Streamlit secrets (works on Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and env_var in st.secrets:
            val = st.secrets[env_var]
            if val:
                return val
    except:
        pass
    
    # 2️⃣ Try encrypted vault (local machine)
    vault = _get_vault()
    if env_var in vault and vault[env_var]:
        return vault[env_var]
    
    # 3️⃣ Try environment variable
    key = os.getenv(env_var)
    if key:
        return key
    
    # 4️⃣ Try .env file (legacy fallback)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith(env_var + "="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    return None

# ── Provider implementations ──

def call_groq(messages, model="llama-3.1-8b-instant", temperature=0.7):
    """Call Groq API with Llama/Mixtral models."""
    try:
        from groq import Groq
        api_key = get_api_key("groq")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=4096
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Groq error: {e}")

def call_gemini(messages, model="gemini-2.0-flash", temperature=0.7):
    """Call Google Gemini API."""
    try:
        import google.generativeai as genai
        api_key = get_api_key("gemini")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        genai.configure(api_key=api_key)
        
        # Extract system prompt
        system_msg = ""
        user_msgs = []
        for m in messages:
            if m["role"] == "system":
                system_msg += m["content"] + "\n"
            else:
                user_msgs.append(m["content"])
        
        model_obj = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_msg.strip() if system_msg else None
        )
        response = model_obj.generate_content("\n".join(user_msgs))
        return response.text
    except Exception as e:
        raise Exception(f"Gemini error: {e}")

def call_openai(messages, model="gpt-4o-mini", temperature=0.7):
    """Call OpenAI API."""
    try:
        from openai import OpenAI
        api_key = get_api_key("openai")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=4096
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI error: {e}")

def call_deepseek(messages, model="deepseek-chat", temperature=0.7):
    """Call DeepSeek API."""
    try:
        from openai import OpenAI as DeepSeekClient
        api_key = get_api_key("deepseek")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found")
        client = DeepSeekClient(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=4096
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"DeepSeek error: {e}")

# ── Provider registry ──

PROVIDERS = {
    "groq": call_groq,
    "gemini": call_gemini,
    "openai": call_openai,
    "deepseek": call_deepseek,
}

# ── Smart call with fallback ──

def call_llm(messages, provider=None, model=None, temperature=0.7, use_fallback=True):
    """
    Call LLM with automatic fallback chain.
    If first provider fails, tries next in chain.
    """
    if provider and provider in PROVIDERS:
        fn = PROVIDERS[provider]
        try:
            return fn(messages, model=model or CONFIG.get("models", {}).get(f"{provider}_model", "default"), temperature=temperature)
        except Exception as e:
            if not use_fallback:
                raise e
            error_msg = str(e)
            print(f"⚠️ {provider} failed: {error_msg[:100]}... Trying fallback...")
    
    # Fallback chain
    for fallback in FALLBACK_CHAIN:
        fb_provider = fallback["provider"]
        fb_model = fallback["model"]
        if fb_provider == provider:
            continue  # skip the one that already failed
        if fb_provider in PROVIDERS:
            fn = PROVIDERS[fb_provider]
            try:
                print(f"🔄 Fallback to {fb_provider}/{fb_model}")
                return fn(messages, model=fb_model, temperature=temperature)
            except Exception as e:
                print(f"⚠️ {fb_provider} also failed: {str(e)[:100]}")
                continue
    
    # Ultimate fallback — return a simple response
    return "⚠️ सभी LLM providers failed हो गए। कृपया अपनी API keys check करें और internet connection verify करें।"

# ── Parse model string like "groq/llama-3.1-8b-instant" ──

def parse_model_string(model_str):
    """Parse 'groq/llama-3.1-8b-instant' into (provider, model_name)."""
    if "/" in model_str:
        parts = model_str.split("/", 1)
        return parts[0], parts[1]
    return "groq", model_str
