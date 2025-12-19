"""Test advanced logger features"""

from logger import UniversalLogger, get_logger

# Test subdirectory logging
print("=== Testing Subdirectory Logging ===")
ai_logger = UniversalLogger("ai_chat", subdir="ai_conversations", level="DEBUG")
api_logger = UniversalLogger("api_calls", subdir="api_logs", level="INFO")

# Test AI logger
ai_logger.ai([
    {"role": "user", "content": "Create a Python function"},
    {"role": "assistant", "content": "I'll create a function for you"}
])

# Test API logger
api_logger.info({"endpoint": "/api/chat", "status": 200, "duration": "1.2s"})
api_logger.rich([
    {"request": "POST /chat", "status": "✅"},
    {"request": "GET /status", "status": "✅"}
])

# Test level filtering
print("\n=== Testing Level Filtering ===")
prod_logger = UniversalLogger("production", level="PROD", enable_rich=False)
prod_logger.debug("This won't show")  # Below PROD level
prod_logger.dev("This won't show")    # Below PROD level
prod_logger.info("This won't show")   # Below PROD level
prod_logger.prod("This WILL show")    # At PROD level
prod_logger.warning("This WILL show") # Above PROD level
prod_logger.error("This WILL show")   # Above PROD level

# Test convenience function
print("\n=== Testing Convenience Function ===")
quick_log = get_logger("quick", subdir="quick_tests")
quick_log.info("Quick logger test")
quick_log.rich({"feature": "convenience", "works": True})

# Test dynamic level changing
print("\n=== Testing Dynamic Level Change ===")
dynamic_log = UniversalLogger("dynamic", level="ERROR")
dynamic_log.info("This won't show initially")
dynamic_log.error("This will show")

dynamic_log.set_level("INFO")
dynamic_log.info("Now this shows after level change")

print("\n=== Advanced tests complete ===")