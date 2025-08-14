"""
Test command that deliberately throws an error (for testing error handling).
Remove this file in production!
"""

from commands import register_exact, wrapped


@wrapped
async def test_error_handler(self, message, cmd, args):
    """Handle !testerror command - deliberately throws an error."""
    if args == "division":
        # Test division by zero
        result = 1 / 0
    elif args == "attribute":
        # Test attribute error
        nonexistent = None
        nonexistent.some_method()
    elif args == "network":
        # Test network error simulation
        raise ConnectionError("Simulated network failure")
    else:
        # Generic error
        raise RuntimeError("Test error for error handling validation")


# Register test error command (remove in production!)
register_exact("testerror", ["testerror"], test_error_handler)