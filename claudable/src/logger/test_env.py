"""Test environment detection"""

import os
from logger import UniversalLogger

# Test different environments
print("=== Testing Environment Detection ===\n")

# Test 1: Default (should detect DEBUG since we're in terminal)
log1 = UniversalLogger("default")
print(f"Default environment level: {log1.level}")

# Test 2: Force DEV environment
os.environ['DEV'] = '1'
log2 = UniversalLogger("dev_env")
print(f"DEV environment level: {log2.level}")
del os.environ['DEV']

# Test 3: Force PROD environment  
os.environ['PRODUCTION'] = '1'
log3 = UniversalLogger("prod_env")
print(f"PROD environment level: {log3.level}")
del os.environ['PRODUCTION']

# Test 4: Test without rich (simulate server environment)
log4 = UniversalLogger("no_rich", enable_rich=False)
log4.info("This is plain text output")
log4.ai([{"role": "user", "content": "Test without rich"}])

print("\n=== Environment detection complete ===")