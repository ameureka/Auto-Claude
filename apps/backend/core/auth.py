"""
Authentication helpers for Auto Claude.

Provides centralized authentication token resolution with fallback support
for multiple environment variables, and SDK environment variable passthrough
for custom API endpoints.
"""

import json
import os
import platform
import subprocess

# Priority order for auth token resolution
# NOTE: ANTHROPIC_API_KEY added for direct API access (use with caution - will incur API costs)
AUTH_TOKEN_ENV_VARS = [
    "CLAUDE_CODE_OAUTH_TOKEN",  # OAuth token from Claude Code CLI (highest priority)
    "ANTHROPIC_AUTH_TOKEN",     # CCR/proxy token (for enterprise/proxy setups)
    "ANTHROPIC_API_KEY",        # Direct API key (lowest priority - incurs costs)
]

# Environment variables to pass through to SDK subprocess
SDK_ENV_VARS = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_API_KEY",
    "NO_PROXY",
    "DISABLE_TELEMETRY",
    "DISABLE_COST_WARNINGS",
    "API_TIMEOUT_MS",
]


def get_token_from_keychain() -> str | None:
    """
    Get authentication token from macOS Keychain.

    Reads Claude Code credentials from macOS Keychain and extracts the OAuth token.
    Only works on macOS (Darwin platform).

    Returns:
        Token string if found in Keychain, None otherwise
    """
    # Only attempt on macOS
    if platform.system() != "Darwin":
        return None

    try:
        # Query macOS Keychain for Claude Code credentials
        result = subprocess.run(
            [
                "/usr/bin/security",
                "find-generic-password",
                "-s",
                "Claude Code-credentials",
                "-w",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return None

        # Parse JSON response
        credentials_json = result.stdout.strip()
        if not credentials_json:
            return None

        data = json.loads(credentials_json)

        # Extract OAuth token from nested structure
        token = data.get("claudeAiOauth", {}).get("accessToken")

        if not token:
            return None

        # Validate token format (Claude OAuth tokens start with sk-ant-oat01-)
        if not token.startswith("sk-ant-oat01-"):
            return None

        return token

    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, Exception):
        # Silently fail - this is a fallback mechanism
        return None


def get_auth_token() -> str | None:
    """
    Get authentication token from environment variables or macOS Keychain.

    Checks multiple sources in priority order:
    1. CLAUDE_CODE_OAUTH_TOKEN (env var)
    2. ANTHROPIC_AUTH_TOKEN (CCR/proxy env var for enterprise setups)
    3. macOS Keychain (if on Darwin platform)

    NOTE: ANTHROPIC_API_KEY is intentionally NOT supported to prevent
    silent billing to user's API credits when OAuth is misconfigured.

    Returns:
        Token string if found, None otherwise
    """
    # First check environment variables
    for var in AUTH_TOKEN_ENV_VARS:
        token = os.environ.get(var)
        if token:
            return token

    # Fallback to macOS Keychain
    return get_token_from_keychain()


def get_auth_token_source() -> str | None:
    """Get the name of the source that provided the auth token."""
    # Check environment variables first
    for var in AUTH_TOKEN_ENV_VARS:
        if os.environ.get(var):
            return var

    # Check if token came from macOS Keychain
    if get_token_from_keychain():
        return "macOS Keychain"

    return None


def require_auth_token() -> str:
    """
    Get authentication token or raise ValueError.

    Raises:
        ValueError: If no auth token is found in any supported source
    """
    token = get_auth_token()
    if not token:
        error_msg = (
            "No authentication token found.\n\n"
            "Auto Claude supports the following authentication methods:\n\n"
            "  1. OAuth Token (recommended):\n"
            "     Run: claude setup-token\n"
        )
        if platform.system() == "Darwin":
            error_msg += "     Token will be saved to macOS Keychain automatically\n"
        error_msg += (
            "     Or set CLAUDE_CODE_OAUTH_TOKEN in .env\n\n"
            "  2. API Key (direct billing):\n"
            "     Set ANTHROPIC_API_KEY in .env\n"
            "     ⚠️  Warning: API costs charged to your account\n\n"
            "  3. Proxy/Enterprise:\n"
            "     Set ANTHROPIC_AUTH_TOKEN + ANTHROPIC_BASE_URL in .env\n"
        )
        raise ValueError(error_msg)
    return token


def get_sdk_env_vars() -> dict[str, str]:
    """
    Get environment variables to pass to SDK.

    Collects relevant env vars (ANTHROPIC_BASE_URL, etc.) that should
    be passed through to the claude-agent-sdk subprocess.

    Returns:
        Dict of env var name -> value for non-empty vars
    """
    env = {}
    for var in SDK_ENV_VARS:
        value = os.environ.get(var)
        if value:
            env[var] = value
    return env


def ensure_claude_code_oauth_token() -> None:
    """
    Ensure CLAUDE_CODE_OAUTH_TOKEN is set (for SDK compatibility).

    If not set but other auth tokens are available, copies the value
    to CLAUDE_CODE_OAUTH_TOKEN so the underlying SDK can use it.
    """
    if os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        return

    token = get_auth_token()
    if token:
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token


def get_token_type(token: str | None) -> str:
    """
    Detect token type based on prefix.

    Returns:
        "oauth" - OAuth Token (sk-ant-oat01-)
        "api_key" - API Key (sk-ant-api-)
        "proxy" - Proxy/Enterprise Token (pc_ / ccr_)
        "unknown" - Unknown type
    """
    if not token:
        return "unknown"

    if token.startswith("sk-ant-oat01-") or token.startswith("sk-ant-oat"):
        return "oauth"
    elif token.startswith("sk-ant-api") or (token.startswith("sk-") and "oat" not in token):
        return "api_key"
    elif token.startswith("pc_") or token.startswith("ccr-"):
        return "proxy"
    return "unknown"


def apply_auth_env(token: str) -> str:
    """
    Set authentication environment variables uniformly.

    CRITICAL: claude-agent-sdk only reads CLAUDE_CODE_OAUTH_TOKEN,
    so all token types must be written to this variable.

    Args:
        token: The authentication token

    Returns:
        Token type string ("oauth", "api_key", "proxy", "unknown")
    """
    token_type = get_token_type(token)

    # Clear potential conflicting variables
    for key in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        os.environ.pop(key, None)

    # CORE: Write to the unified entry point that SDK reads
    os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token

    # Also set the native variable for the token type (for logging/debugging)
    if token_type == "api_key":
        os.environ["ANTHROPIC_API_KEY"] = token
    elif token_type == "proxy":
        os.environ["ANTHROPIC_AUTH_TOKEN"] = token

    return token_type


def is_api_key_mode() -> bool:
    """Check if currently using API Key mode."""
    token = get_auth_token()
    return get_token_type(token) == "api_key"


def validate_proxy_config() -> tuple[bool, str]:
    """
    Validate Proxy configuration completeness.

    Returns:
        (is_valid, error_message)
    """
    token = get_auth_token()
    if get_token_type(token) != "proxy":
        return True, ""

    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    if not base_url:
        return False, "Proxy token detected but ANTHROPIC_BASE_URL is not set"
    return True, ""
