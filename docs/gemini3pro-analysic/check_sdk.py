import inspect
try:
    from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
    print("Successfully imported claude_agent_sdk")
    
    # Check ClaudeAgentOptions
    sig = inspect.signature(ClaudeAgentOptions)
    print("\nClaudeAgentOptions signature:")
    print(sig)
    
    # Check docstrings if possible
    print("\nClaudeAgentOptions docstring:")
    print(ClaudeAgentOptions.__doc__)
    
except ImportError:
    print("Could not import claude_agent_sdk. It might not be installed in this environment.")
except Exception as e:
    print(f"An error occurred: {e}")

