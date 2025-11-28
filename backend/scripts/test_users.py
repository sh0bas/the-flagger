import httpx
import asyncio
import sys

BASE_URL = "http://localhost:8000/api"

async def test_user_flow():
    async with httpx.AsyncClient() as client:
        # 1. Login (assuming user exists from previous test)
        print("Logging in...")
        login_data = {
            "username": "autotestuser",
            "password": "Password123!"
        }
        response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} {response.text}")
            # Try registering if login fails
            print("Registering...")
            register_data = {
                "username": "autotestuser",
                "email": "autotest@example.com",
                "password": "Password123!",
                "display_name": "Auto Test User"
            }
            await client.post(f"{BASE_URL}/auth/register", json=register_data)
            response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code != 200:
                print("Login failed after registration")
                sys.exit(1)
        
        tokens = response.json()
        access_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Get Current User
        print("\nGetting Current User...")
        response = await client.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"User: {user['username']} ({user['display_name']})")
        else:
            print(f"Get Me failed: {response.status_code} {response.text}")
            sys.exit(1)
            
        # 3. Update Profile
        print("\nUpdating Profile...")
        update_data = {
            "display_name": "Updated Test User"
        }
        response = await client.patch(f"{BASE_URL}/users/me", json=update_data, headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"Updated Name: {user['display_name']}")
            if user['display_name'] != "Updated Test User":
                print("Update failed: Name mismatch")
                sys.exit(1)
        else:
            print(f"Update failed: {response.status_code} {response.text}")
            sys.exit(1)
            
        # 4. Search Users
        print("\nSearching Users...")
        response = await client.get(f"{BASE_URL}/users/search?q=Updated", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"Found {len(users)} users")
            found = any(u['username'] == 'autotestuser' for u in users)
            if found:
                print("Found self in search")
            else:
                print("Did not find self in search")
        else:
            print(f"Search failed: {response.status_code} {response.text}")
            sys.exit(1)
            
        # 5. Get Public Profile
        print("\nGetting Public Profile...")
        response = await client.get(f"{BASE_URL}/users/autotestuser", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"Public Profile: {user['username']}")
        else:
            print(f"Get Public Profile failed: {response.status_code} {response.text}")
            sys.exit(1)
            
        print("\nAll User Tests Passed!")

if __name__ == "__main__":
    asyncio.run(test_user_flow())
