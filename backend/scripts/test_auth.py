import httpx
import sys
import asyncio

BASE_URL = "http://localhost:8000/api/auth"

async def test_auth_flow():
    async with httpx.AsyncClient() as client:
        # 1. Register
        print("Testing Registration...")
        register_data = {
            "username": "autotestuser",
            "email": "autotest@example.com",
            "password": "Password123!",
            "display_name": "Auto Test User"
        }
        response = await client.post(f"{BASE_URL}/register", json=register_data)
        if response.status_code == 201:
            print("Registration successful")
        elif response.status_code == 400 and ("already registered" in response.text or "Username already taken" in response.text):
            print("User already registered, proceeding...")
        else:
            print(f"Registration failed: {response.status_code} {response.text}")
            sys.exit(1)

        # 2. Login
        print("\nTesting Login...")
        login_data = {
            "username": "autotestuser",
            "password": "Password123!"
        }
        response = await client.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            print("Login successful")
            tokens = response.json()
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
            print(f"Access Token: {access_token[:20]}...")
            print(f"Refresh Token: {refresh_token[:20]}...")
        else:
            print(f"Login failed: {response.status_code} {response.text}")
            sys.exit(1)

        # 3. Refresh Token
        print("\nTesting Token Refresh...")
        refresh_data = {
            "refresh_token": refresh_token
        }
        response = await client.post(f"{BASE_URL}/refresh", json=refresh_data)
        if response.status_code == 200:
            print("Token refresh successful")
            new_tokens = response.json()
            print(f"New Access Token: {new_tokens['access_token'][:20]}...")
        else:
            print(f"Token refresh failed: {response.status_code} {response.text}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
