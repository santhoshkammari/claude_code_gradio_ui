import asyncio
import aiohttp
import json

async def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("Testing Claude FastAPI endpoints...")
    
    # Test health check
    async with aiohttp.ClientSession() as session:
        print("\n1. Testing health check endpoint...")
        async with session.get(f"{base_url}/health") as response:
            health_data = await response.json()
            print(f"Health: {health_data}")
    
        print("\n2. Testing session creation...")
        create_data = {
            "profile": "dev",
            "system_prompt": "You are a helpful assistant",
            "allowed_tools": ["Read", "Write", "Bash"],
            "permission_mode": "acceptEdits",
            "model": "claude-sonnet-4.5"
        }
        
        async with session.post(f"{base_url}/sessions", json=create_data) as response:
            if response.status == 200:
                session_data = await response.json()
                session_id = session_data["session_id"]
                print(f"Created session: {session_id}")
            else:
                print(f"Failed to create session: {response.status}")
                error_text = await response.text()
                print(f"Error: {error_text}")
                return
    
        print(f"\n3. Testing session info retrieval...")
        async with session.get(f"{base_url}/sessions/{session_id}") as response:
            if response.status == 200:
                info_data = await response.json()
                print(f"Session info: {info_data['session_id']}, status: {info_data['status']}")
            else:
                print(f"Failed to get session info: {response.status}")
    
        print(f"\n4. Testing query endpoint...")
        query_data = {
            "prompt": "Hello, Claude! How are you today?"
        }
        
        async with session.post(f"{base_url}/sessions/{session_id}/query", json=query_data) as response:
            if response.status == 200:
                query_result = await response.json()
                print(f"Query accepted: {query_result}")
            else:
                print(f"Failed to send query: {response.status}")
                error_text = await response.text()
                print(f"Error: {error_text}")
    
        print(f"\n5. Testing interrupt endpoint...")
        interrupt_data = {}
        
        async with session.post(f"{base_url}/sessions/{session_id}/interrupt", json=interrupt_data) as response:
            if response.status in [200, 409, 400]:  # 409 might occur if nothing to interrupt
                interrupt_result = await response.json()
                print(f"Interrupt result: {interrupt_result}")
            else:
                print(f"Failed to interrupt: {response.status}")
    
        print(f"\n6. Testing reset endpoint...")
        reset_data = {
            "hard_reset": False
        }
        
        async with session.post(f"{base_url}/sessions/{session_id}/reset", json=reset_data) as response:
            if response.status == 200:
                reset_result = await response.json()
                print(f"Reset result: {reset_result}")
            else:
                print(f"Failed to reset: {response.status}")
    
        print(f"\n7. Testing session deletion...")
        async with session.delete(f"{base_url}/sessions/{session_id}") as response:
            if response.status == 200:
                delete_result = await response.json()
                print(f"Delete result: {delete_result}")
            else:
                print(f"Failed to delete session: {response.status}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(test_endpoints())