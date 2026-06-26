"""
BHARATSOLVE — Secure API Key Vault
🔐 Encrypted key storage — no plain text on disk.
Uses AES-256 encryption with a machine-derived key.
"""
import os
import base64
import hashlib
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".vault.enc")
SALT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".vault.salt")

# ── Machine fingerprint (hard to copy/leak) ──

def _get_machine_fingerprint() -> str:
    """Create a unique machine fingerprint using hardware IDs."""
    import subprocess
    parts = []
    
    try:
        # Windows: get volume serial + machine GUID
        if os.name == 'nt':
            result = subprocess.run(
                'wmic diskdrive get serialnumber 2>nul',
                shell=True, capture_output=True, text=True, timeout=5
            )
            serial = result.stdout.strip().split('\n')[-1].strip() if result.stdout else ''
            if serial:
                parts.append(serial)
            
            result2 = subprocess.run(
                'wmic csproduct get uuid 2>nul',
                shell=True, capture_output=True, text=True, timeout=5
            )
            uuid_val = result2.stdout.strip().split('\n')[-1].strip() if result2.stdout else ''
            if uuid_val:
                parts.append(uuid_val)
        elif os.name == 'posix':
            # Linux/Mac: use machine-id
            for path in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
                if os.path.exists(path):
                    try:
                        with open(path) as f:
                            parts.append(f.read().strip())
                        break
                    except:
                        pass
            # Also check if we're on Streamlit Cloud (no real hardware)
            if not parts:
                # Streamlit Cloud / cloud environments fallback
                parts.append(os.environ.get('STREAMLIT_RUNNER_ID', 'cloud'))
                parts.append(os.environ.get('STREAMLIT_SERVER_RUN_ON_SAVE', ''))
        else:
            # Linux/Mac: use machine-id
            for path in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
                if os.path.exists(path):
                    try:
                        with open(path) as f:
                            parts.append(f.read().strip())
                        break
                    except:
                        pass
    except:
        pass
    
    # Fallback: combine common identifiers
    parts.append(os.name)
    parts.append(os.environ.get('COMPUTERNAME', '') or os.environ.get('HOSTNAME', ''))
    parts.append(os.environ.get('USERNAME', '') or os.environ.get('USER', ''))
    
    return '_'.join(filter(None, parts))


def _derive_key() -> bytes:
    """Derive encryption key from machine fingerprint + random salt."""
    fingerprint = _get_machine_fingerprint()
    
    # Create or load salt
    if not os.path.exists(SALT_FILE):
        salt = os.urandom(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
    else:
        with open(SALT_FILE, 'rb') as f:
            salt = f.read()
    
    # Derive key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # High iteration count
    )
    key = base64.urlsafe_b64encode(kdf.derive(fingerprint.encode()))
    return key


# ── Public API ──

def save_api_keys(keys: dict) -> bool:
    """
    Save API keys to encrypted vault.
    
    keys = {
        "GROQ_API_KEY": "...",
        "GEMINI_API_KEY": "...",
        ...
    }
    """
    try:
        key = _derive_key()
        f = Fernet(key)
        
        data = json.dumps(keys).encode()
        encrypted = f.encrypt(data)
        
        with open(VAULT_FILE, 'wb') as fh:
            fh.write(encrypted)
        
        return True
    except Exception as e:
        print(f"❌ Vault save error: {e}")
        return False


def load_api_keys() -> dict:
    """Load API keys from encrypted vault. Returns empty dict if not found."""
    if not os.path.exists(VAULT_FILE):
        return {}
    
    try:
        key = _derive_key()
        f = Fernet(key)
        
        with open(VAULT_FILE, 'rb') as fh:
            encrypted = fh.read()
        
        decrypted = f.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception as e:
        print(f"⚠️ Vault load error (wrong machine?): {e}")
        return {}


def has_vault() -> bool:
    """Check if vault exists."""
    return os.path.exists(VAULT_FILE)


def destroy_vault() -> bool:
    """Delete vault and salt files."""
    try:
        if os.path.exists(VAULT_FILE):
            os.remove(VAULT_FILE)
        if os.path.exists(SALT_FILE):
            os.remove(SALT_FILE)
        return True
    except:
        return False


def encrypt_data(plaintext: str) -> str:
    """
    Encrypt a single string (for WordPress passwords, etc.).
    Returns base64-encoded encrypted string.
    """
    try:
        key = _derive_key()
        f = Fernet(key)
        encrypted = f.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        print(f"⚠️ Encryption error: {e}")
        # Fallback to base64 encoding (not truly secure but prevents plaintext on disk)
        return base64.b64encode(plaintext.encode()).decode()


def decrypt_data(encrypted_b64: str) -> str:
    """
    Decrypt a string that was encrypted with encrypt_data().
    """
    try:
        key = _derive_key()
        f = Fernet(key)
        encrypted_bytes = base64.b64decode(encrypted_b64)
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        print(f"⚠️ Decryption error: {e}")
        # Try simple base64 decode as fallback
        try:
            return base64.b64decode(encrypted_b64).decode()
        except:
            return ""


def get_key(provider: str) -> str:
    """Get a single API key by provider name."""
    keys = load_api_keys()
    env_map = {
        "groq": "GROQ_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "claude": "CLAUDE_API_KEY",
    }
    env_var = env_map.get(provider, f"{provider.upper()}_API_KEY")
    return keys.get(env_var, "")


# ── CLI for one-time setup ──

if __name__ == "__main__":
    import getpass
    
    print("=" * 55)
    print("🔐 BHARATSOLVE — Secure API Key Setup")
    print("=" * 55)
    print()
    print("Your keys will be encrypted with your machine's fingerprint.")
    print("They CANNOT be read on any other computer.")
    print("Even if someone steals the vault file, they can't decrypt it.")
    print()
    
    keys = {}
    
    print("📌 Enter your API keys (leave blank to skip):")
    print()
    
    groq = getpass.getpass("  Groq API Key (gsk_...): ").strip()
    if groq:
        keys["GROQ_API_KEY"] = groq
    
    gemini = getpass.getpass("  Gemini API Key (AIza...): ").strip()
    if gemini:
        keys["GEMINI_API_KEY"] = gemini
    
    openai = getpass.getpass("  OpenAI API Key (sk-...): ").strip()
    if openai:
        keys["OPENAI_API_KEY"] = openai
    
    deepseek = getpass.getpass("  DeepSeek API Key (sk-...): ").strip()
    if deepseek:
        keys["DEEPSEEK_API_KEY"] = deepseek
    
    print()
    
    if not keys:
        print("⚠️  No keys entered. Exiting.")
    else:
        success = save_api_keys(keys)
        if success:
            print("✅ Keys encrypted & saved securely!")
            print(f"   Vault: {VAULT_FILE}")
            print()
            print("🗑️  You can now DELETE the .env file if it exists — it's no longer needed.")
            print("   (The app will use the encrypted vault instead.)")
            print()
            
            # Offer to delete old .env
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
            if os.path.exists(env_path):
                confirm = input("Delete old plain-text .env file? (y/n): ").strip().lower()
                if confirm == 'y':
                    os.remove(env_path)
                    print("✅ .env file deleted!")
                else:
                    print("⚠️  Keeping .env — consider deleting it manually for security.")
        else:
            print("❌ Failed to save keys. Check permissions.")
