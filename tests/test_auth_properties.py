"""
Property-based tests for authentication module.

Uses Hypothesis for property testing to verify:
- Property 1: Token Classification Correctness (Task 1.4)
- Validates Requirements 1.1, 1.2, 1.3, 1.4
"""

import os
import sys

import pytest
from hypothesis import given, strategies as st, settings

# Add apps/backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "backend"))

from core.auth import get_token_type


# =============================================================================
# Property 1: Token Classification Correctness (Task 1.4)
# =============================================================================


class TestTokenClassificationProperty:
    """
    Property 1: Token Classification Correctness
    
    For any token string, get_token_type SHALL return:
    - "oauth" if and only if token starts with sk-ant-oat01- or sk-ant-oat
    - "api_key" if and only if token starts with sk-ant-api, OR (starts with sk- AND NOT starts with sk-ant-oat)
    - "proxy" if and only if token starts with pc_ or ccr-
    - "unknown" for all other cases
    
    Validates: Requirements 1.1, 1.2, 1.3, 1.4
    """

    @given(st.text())
    @settings(max_examples=200)
    def test_token_classification_exhaustive(self, token: str):
        """Property test: classification result must match prefix rules."""
        result = get_token_type(token)
        
        # Result must be one of the valid types
        assert result in ("oauth", "api_key", "proxy", "unknown")
        
        # Verify classification rules (order matters!)
        # OAuth prefixes must be checked before generic sk- prefix
        if token.startswith("sk-ant-oat01-") or token.startswith("sk-ant-oat"):
            assert result == "oauth", f"Token '{token[:30]}...' should be oauth"
        elif token.startswith("sk-ant-api"):
            assert result == "api_key", f"Token '{token[:30]}...' should be api_key"
        elif token.startswith("sk-") and not token.startswith("sk-ant-oat"):
            assert result == "api_key", f"Token '{token[:30]}...' should be api_key (generic sk-)"
        elif token.startswith("pc_") or token.startswith("ccr-"):
            assert result == "proxy", f"Token '{token[:30]}...' should be proxy"
        else:
            assert result == "unknown", f"Token '{token[:30]}...' should be unknown"

    def test_oauth_token_classification(self):
        """Explicit test: OAuth tokens are correctly classified."""
        # sk-ant-oat01- prefix
        assert get_token_type("sk-ant-oat01-abc123") == "oauth"
        assert get_token_type("sk-ant-oat01-") == "oauth"
        
        # sk-ant-oat prefix (shorter variant)
        assert get_token_type("sk-ant-oat-xyz") == "oauth"
        assert get_token_type("sk-ant-oat") == "oauth"

    def test_api_key_classification(self):
        """Explicit test: API Key tokens are correctly classified."""
        # sk-ant-api prefix
        assert get_token_type("sk-ant-api03-abc123") == "api_key"
        assert get_token_type("sk-ant-api-") == "api_key"
        
        # Generic sk- prefix (excluding oat)
        assert get_token_type("sk-abc123") == "api_key"
        assert get_token_type("sk-test-key") == "api_key"

    def test_proxy_token_classification(self):
        """Explicit test: Proxy tokens are correctly classified."""
        # pc_ prefix
        assert get_token_type("pc_abc123") == "proxy"
        assert get_token_type("pc_") == "proxy"
        
        # ccr- prefix
        assert get_token_type("ccr-abc123") == "proxy"
        assert get_token_type("ccr-") == "proxy"

    def test_unknown_token_classification(self):
        """Explicit test: Unknown tokens return 'unknown'."""
        assert get_token_type("") == "unknown"
        assert get_token_type("random-token") == "unknown"
        assert get_token_type("api-key-123") == "unknown"
        assert get_token_type(None) == "unknown"

    def test_oauth_priority_over_generic_sk(self):
        """Ensure OAuth prefixes are checked before generic sk- prefix."""
        # This is critical: sk-ant-oat starts with sk- but should be oauth
        token = "sk-ant-oat01-should-be-oauth"
        assert get_token_type(token) == "oauth"
        
        token = "sk-ant-oat-should-be-oauth"
        assert get_token_type(token) == "oauth"

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Partial prefixes
        assert get_token_type("sk-an") == "api_key"  # starts with sk- but not oat
        assert get_token_type("sk-ant") == "api_key"  # starts with sk- but not oat
        assert get_token_type("pc") == "unknown"  # missing underscore
        assert get_token_type("ccr") == "unknown"  # missing dash
        
        # Mixed case (should not match - case sensitive)
        assert get_token_type("SK-ANT-OAT01-abc") == "unknown"
        assert get_token_type("PC_abc") == "unknown"


# =============================================================================
# Property 2: Type-Specific Environment Injection (Task 2.2)
# =============================================================================


class TestTypeSpecificInjectionProperty:
    """
    Property 2: Type-Specific Environment Injection
    
    For any valid token string, after calling apply_auth_env(token):
    - IF token type is oauth, THEN CLAUDE_CODE_OAUTH_TOKEN SHALL equal the input token
    - IF token type is api_key, THEN ANTHROPIC_API_KEY SHALL equal the input token
    - IF token type is proxy, THEN ANTHROPIC_AUTH_TOKEN SHALL equal the input token
    - IF token type is unknown, THEN CLAUDE_CODE_OAUTH_TOKEN SHALL equal the input token (fallback)
    
    Validates: Requirements 2.1, 2.2, 2.3
    """

    def setup_method(self):
        """Clear environment before each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Clean up environment after each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
            os.environ.pop(var, None)

    @given(st.text(min_size=1))
    @settings(max_examples=100)
    def test_type_specific_injection(self, token: str):
        """Property test: token is written to type-specific variable."""
        from hypothesis import assume
        from core.auth import apply_auth_env
        
        # Filter out tokens with null bytes (invalid for env vars)
        assume('\x00' not in token)
        
        # Clear environment first
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
            os.environ.pop(var, None)
        
        token_type = apply_auth_env(token)
        
        # All tokens get written to CLAUDE_CODE_OAUTH_TOKEN (SDK entry point)
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == token
        
        # Type-specific native variable is also set
        if token_type == "api_key":
            assert os.environ.get("ANTHROPIC_API_KEY") == token
        elif token_type == "proxy":
            assert os.environ.get("ANTHROPIC_AUTH_TOKEN") == token

    def test_oauth_injection(self):
        """OAuth token should write to CLAUDE_CODE_OAUTH_TOKEN only."""
        from core.auth import apply_auth_env
        
        result = apply_auth_env("sk-ant-oat01-test")
        assert result == "oauth"
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "sk-ant-oat01-test"
        # No native variable for oauth (it IS the native variable)
        assert os.environ.get("ANTHROPIC_API_KEY") is None
        assert os.environ.get("ANTHROPIC_AUTH_TOKEN") is None

    def test_api_key_injection(self):
        """API Key should write to both CLAUDE_CODE_OAUTH_TOKEN and ANTHROPIC_API_KEY."""
        from core.auth import apply_auth_env
        
        result = apply_auth_env("sk-ant-api03-test")
        assert result == "api_key"
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "sk-ant-api03-test"
        assert os.environ.get("ANTHROPIC_API_KEY") == "sk-ant-api03-test"
        assert os.environ.get("ANTHROPIC_AUTH_TOKEN") is None

    def test_proxy_injection(self):
        """Proxy token should write to both CLAUDE_CODE_OAUTH_TOKEN and ANTHROPIC_AUTH_TOKEN."""
        from core.auth import apply_auth_env
        
        result = apply_auth_env("pc_test123")
        assert result == "proxy"
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "pc_test123"
        assert os.environ.get("ANTHROPIC_AUTH_TOKEN") == "pc_test123"
        assert os.environ.get("ANTHROPIC_API_KEY") is None


# =============================================================================
# Property 3: Conflicting Variable Cleanup (Task 2.3)
# =============================================================================


class TestConflictingVariableCleanupProperty:
    """
    Property 3: Conflicting Variable Cleanup
    
    For any initial environment state with conflicting auth variables,
    after calling apply_auth_env(token):
    - Conflicting variables SHALL be cleared before injection
    - Only the correct type-specific variable(s) SHALL be set
    
    Validates: Requirements 2.2, 2.3, 2.4
    """

    def setup_method(self):
        """Clear environment before each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Clean up environment after each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
            os.environ.pop(var, None)

    def test_clears_conflicts_for_oauth(self):
        """Applying OAuth token should clear API Key and Proxy vars."""
        from core.auth import apply_auth_env
        
        # Pre-set conflicting variables
        os.environ["ANTHROPIC_API_KEY"] = "old-api-key"
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "old-proxy-token"
        
        apply_auth_env("sk-ant-oat01-new")
        
        # Old conflicts should be cleared
        assert os.environ.get("ANTHROPIC_API_KEY") is None
        assert os.environ.get("ANTHROPIC_AUTH_TOKEN") is None
        # New token should be set
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "sk-ant-oat01-new"

    def test_clears_conflicts_for_api_key(self):
        """Applying API Key should clear OAuth and Proxy vars."""
        from core.auth import apply_auth_env
        
        # Pre-set conflicting variables
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "old-oauth"
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "old-proxy"
        
        apply_auth_env("sk-ant-api03-new")
        
        # New token should replace old OAuth var
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "sk-ant-api03-new"
        # Proxy should be cleared
        assert os.environ.get("ANTHROPIC_AUTH_TOKEN") is None
        # API Key native var should be set
        assert os.environ.get("ANTHROPIC_API_KEY") == "sk-ant-api03-new"

    def test_clears_conflicts_for_proxy(self):
        """Applying Proxy token should clear OAuth and API Key vars."""
        from core.auth import apply_auth_env
        
        # Pre-set conflicting variables
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "old-oauth"
        os.environ["ANTHROPIC_API_KEY"] = "old-api"
        
        apply_auth_env("pc_new-proxy")
        
        # New token should replace old OAuth var
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "pc_new-proxy"
        # API Key should be cleared
        assert os.environ.get("ANTHROPIC_API_KEY") is None
        # Proxy native var should be set
        assert os.environ.get("ANTHROPIC_AUTH_TOKEN") == "pc_new-proxy"

    @given(st.text(min_size=1))
    @settings(max_examples=50)
    def test_no_stale_variables_after_apply(self, token: str):
        """Property: after apply_auth_env, no stale auth variables exist."""
        from hypothesis import assume
        from core.auth import apply_auth_env
        
        # Filter out tokens with null bytes (invalid for env vars)
        assume('\x00' not in token)
        
        # Pre-populate all variables with "stale" values
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "stale-oauth"
        os.environ["ANTHROPIC_API_KEY"] = "stale-api"
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "stale-proxy"
        
        token_type = apply_auth_env(token)
        
        # CLAUDE_CODE_OAUTH_TOKEN should always be the new token
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == token
        
        # Only the appropriate native variable should be set
        if token_type == "oauth" or token_type == "unknown":
            assert os.environ.get("ANTHROPIC_API_KEY") is None
            assert os.environ.get("ANTHROPIC_AUTH_TOKEN") is None
        elif token_type == "api_key":
            assert os.environ.get("ANTHROPIC_API_KEY") == token
            assert os.environ.get("ANTHROPIC_AUTH_TOKEN") is None
        elif token_type == "proxy":
            assert os.environ.get("ANTHROPIC_API_KEY") is None
            assert os.environ.get("ANTHROPIC_AUTH_TOKEN") == token


# =============================================================================
# Property 4: Priority Resolution Determinism (Task 2.5)
# =============================================================================


class TestPriorityResolutionProperty:
    """
    Property 4: Priority Resolution Determinism
    
    For any environment with multiple auth tokens set, get_auth_token()
    SHALL return the token from the highest priority source:
    CLAUDE_CODE_OAUTH_TOKEN > ANTHROPIC_AUTH_TOKEN > ANTHROPIC_API_KEY
    
    Validates: Requirements 3.1, 3.2
    """

    def setup_method(self):
        """Clear environment before each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Clean up environment after each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
            os.environ.pop(var, None)

    def test_oauth_highest_priority(self):
        """CLAUDE_CODE_OAUTH_TOKEN has highest priority."""
        from core.auth import get_auth_token
        
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "oauth-token"
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "proxy-token"
        os.environ["ANTHROPIC_API_KEY"] = "api-key"
        
        result = get_auth_token()
        assert result == "oauth-token"

    def test_proxy_second_priority(self):
        """ANTHROPIC_AUTH_TOKEN has second priority."""
        from core.auth import get_auth_token
        
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "proxy-token"
        os.environ["ANTHROPIC_API_KEY"] = "api-key"
        
        result = get_auth_token()
        assert result == "proxy-token"

    def test_api_key_lowest_priority(self):
        """ANTHROPIC_API_KEY has lowest priority."""
        from core.auth import get_auth_token
        
        os.environ["ANTHROPIC_API_KEY"] = "api-key"
        
        result = get_auth_token()
        assert result == "api-key"

    def test_empty_returns_none_or_keychain(self):
        """No tokens set returns None (or Keychain on macOS)."""
        from core.auth import get_auth_token
        
        result = get_auth_token()
        # Result is either None or a Keychain token (on macOS)
        if result is not None:
            # If not None, it came from Keychain and should be OAuth format
            assert result.startswith("sk-ant-oat01-")

    @given(
        oauth=st.one_of(st.none(), st.text(min_size=1)),
        proxy=st.one_of(st.none(), st.text(min_size=1)),
        api_key=st.one_of(st.none(), st.text(min_size=1))
    )
    @settings(max_examples=50)
    def test_priority_determinism(self, oauth, proxy, api_key):
        """Property: resolution priority is always deterministic."""
        from hypothesis import assume
        from core.auth import get_auth_token
        
        # Filter out tokens with null bytes (invalid for env vars)
        assume(oauth is None or '\x00' not in oauth)
        assume(proxy is None or '\x00' not in proxy)
        assume(api_key is None or '\x00' not in api_key)
        
        # Set up environment
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
            os.environ.pop(var, None)
        
        if oauth:
            os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = oauth
        if proxy:
            os.environ["ANTHROPIC_AUTH_TOKEN"] = proxy
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        
        result = get_auth_token()
        
        # Verify priority order
        if oauth:
            assert result == oauth
        elif proxy:
            assert result == proxy
        elif api_key:
            assert result == api_key
        # else: result is None or from Keychain


# =============================================================================
# Property 5: Proxy Validation Completeness (Task 3.2)
# =============================================================================


class TestProxyValidationProperty:
    """
    Property 5: Proxy Validation Completeness
    
    For any proxy token (type "proxy"), validate_proxy_config() SHALL return
    (False, error_message) if and only if ANTHROPIC_BASE_URL is not set.
    
    Validates: Requirements 4.1, 4.2
    """

    def setup_method(self):
        """Clear environment before each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Clean up environment after each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def test_proxy_without_base_url_fails(self):
        """Proxy token without ANTHROPIC_BASE_URL should fail validation."""
        from core.auth import validate_proxy_config
        
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "pc_test-proxy"
        # Note: ANTHROPIC_BASE_URL is NOT set
        
        is_valid, error_msg = validate_proxy_config()
        assert is_valid is False
        assert "ANTHROPIC_BASE_URL" in error_msg

    def test_proxy_with_base_url_succeeds(self):
        """Proxy token with ANTHROPIC_BASE_URL should pass validation."""
        from core.auth import validate_proxy_config
        
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "pc_test-proxy"
        os.environ["ANTHROPIC_BASE_URL"] = "http://localhost:8999"
        
        is_valid, error_msg = validate_proxy_config()
        assert is_valid is True
        assert error_msg == ""

    def test_non_proxy_always_passes(self):
        """Non-proxy tokens should always pass validation."""
        from core.auth import validate_proxy_config
        
        # OAuth token
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "sk-ant-oat01-test"
        is_valid, error_msg = validate_proxy_config()
        assert is_valid is True
        os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
        
        # API Key
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-api03-test"
        is_valid, error_msg = validate_proxy_config()
        assert is_valid is True
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_ccr_prefix_also_requires_base_url(self):
        """ccr- prefix tokens should also require ANTHROPIC_BASE_URL."""
        from core.auth import validate_proxy_config
        
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "ccr-test-token"
        # Note: ANTHROPIC_BASE_URL is NOT set
        
        is_valid, error_msg = validate_proxy_config()
        assert is_valid is False
        assert "ANTHROPIC_BASE_URL" in error_msg

    @given(st.text(min_size=1))
    @settings(max_examples=30)
    def test_proxy_validation_determinism(self, base_url: str):
        """Property: validation result is deterministic based on base_url presence."""
        from hypothesis import assume
        from core.auth import validate_proxy_config
        
        assume('\x00' not in base_url)
        
        # Set proxy token
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "pc_property-test"
        os.environ.pop("ANTHROPIC_BASE_URL", None)
        
        # With base_url set
        os.environ["ANTHROPIC_BASE_URL"] = base_url
        is_valid, _ = validate_proxy_config()
        assert is_valid is True
        
        # Without base_url
        os.environ.pop("ANTHROPIC_BASE_URL", None)
        is_valid, error_msg = validate_proxy_config()
        assert is_valid is False
        assert "ANTHROPIC_BASE_URL" in error_msg


# =============================================================================
# Property 6: Backward Compatibility (Task 11.4)
# =============================================================================


class TestBackwardCompatibilityProperty:
    """
    Property 6: Backward Compatibility
    
    For any OAuth token retrieved via the previous implementation path
    (environment variable or Keychain), the new implementation SHALL
    produce identical SDK authentication behavior.
    
    Validates: Requirements 8.1, 8.2, 8.3
    """

    def setup_method(self):
        """Clear environment before each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Clean up environment after each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def test_oauth_only_env_unchanged(self):
        """OAuth-only environment produces identical behavior."""
        from core.auth import get_auth_token, apply_auth_env
        
        # Set up OAuth-only environment (legacy behavior)
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "sk-ant-oat01-legacy-token"
        
        token = get_auth_token()
        assert token == "sk-ant-oat01-legacy-token"
        
        token_type = apply_auth_env(token)
        assert token_type == "oauth"
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "sk-ant-oat01-legacy-token"

    def test_keychain_retrieval_unchanged(self):
        """Keychain retrieval (on macOS) continues to work."""
        from core.auth import get_token_from_keychain
        import platform
        
        if platform.system() != "Darwin":
            # Skip on non-macOS systems
            return
        
        # This test just verifies the function is callable
        # Actual Keychain testing requires real credentials
        result = get_token_from_keychain()
        # Result is either None (no credential) or valid OAuth token
        if result is not None:
            assert result.startswith("sk-ant-oat01-")


# =============================================================================
# Integration Tests (Task 11.1, 11.2, 11.3)
# =============================================================================


class TestOAuthModeIntegration:
    """
    Task 11.1: OAuth Mode Integration Tests
    
    Validates: Requirements 8.1, 8.2
    """

    def setup_method(self):
        """Clear environment before each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Clean up environment after each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def test_oauth_flow_complete(self):
        """Complete OAuth flow works correctly."""
        from core.auth import get_auth_token, get_token_type, apply_auth_env
        
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "sk-ant-oat01-integration-test"
        
        token = get_auth_token()
        assert token == "sk-ant-oat01-integration-test"
        
        token_type = get_token_type(token)
        assert token_type == "oauth"
        
        result_type = apply_auth_env(token)
        assert result_type == "oauth"
        
        # OAuth is set, others are cleared
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "sk-ant-oat01-integration-test"
        assert os.environ.get("ANTHROPIC_API_KEY") is None
        assert os.environ.get("ANTHROPIC_AUTH_TOKEN") is None


class TestApiKeyModeIntegration:
    """
    Task 11.2: API Key Mode Integration Tests
    
    Validates: Requirements 5.1, 5.2
    """

    def setup_method(self):
        """Clear environment before each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Clean up environment after each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def test_api_key_flow_complete(self):
        """Complete API Key flow works correctly."""
        from core.auth import get_auth_token, get_token_type, apply_auth_env, is_api_key_mode
        
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-api03-integration-test"
        
        token = get_auth_token()
        assert token == "sk-ant-api03-integration-test"
        
        assert is_api_key_mode() is True
        
        token_type = get_token_type(token)
        assert token_type == "api_key"
        
        result_type = apply_auth_env(token)
        assert result_type == "api_key"
        
        # Both unified entry point and native variable are set
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "sk-ant-api03-integration-test"
        assert os.environ.get("ANTHROPIC_API_KEY") == "sk-ant-api03-integration-test"
        assert os.environ.get("ANTHROPIC_AUTH_TOKEN") is None


class TestProxyModeIntegration:
    """
    Task 11.3: Proxy Mode Integration Tests
    
    Validates: Requirements 4.1, 4.2, 4.3
    """

    def setup_method(self):
        """Clear environment before each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Clean up environment after each test."""
        for var in ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
            os.environ.pop(var, None)

    def test_proxy_flow_complete(self):
        """Complete Proxy flow works correctly with base URL."""
        from core.auth import get_auth_token, get_token_type, apply_auth_env, validate_proxy_config
        
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "pc_integration-test"
        os.environ["ANTHROPIC_BASE_URL"] = "http://localhost:8999"
        
        token = get_auth_token()
        assert token == "pc_integration-test"
        
        token_type = get_token_type(token)
        assert token_type == "proxy"
        
        # Validate proxy config
        is_valid, _ = validate_proxy_config()
        assert is_valid is True
        
        result_type = apply_auth_env(token)
        assert result_type == "proxy"
        
        # Both unified entry point and native variable are set
        assert os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") == "pc_integration-test"
        assert os.environ.get("ANTHROPIC_AUTH_TOKEN") == "pc_integration-test"
        assert os.environ.get("ANTHROPIC_API_KEY") is None

    def test_proxy_without_base_url_fails(self):
        """Proxy mode without base URL fails validation."""
        from core.auth import validate_proxy_config
        
        os.environ["ANTHROPIC_AUTH_TOKEN"] = "pc_integration-test"
        # ANTHROPIC_BASE_URL is NOT set
        
        is_valid, error_msg = validate_proxy_config()
        assert is_valid is False
        assert "ANTHROPIC_BASE_URL" in error_msg
