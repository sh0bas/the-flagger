import httpx
import asyncio
import sys

BASE_URL = "http://localhost:8000/api"

async def test_game_flow():
    async with httpx.AsyncClient() as client:
        # 1. Login
        print("Logging in...")
        login_data = {
            "username": "autotestuser",
            "password": "Password123!"
        }
        response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} {response.text}")
            sys.exit(1)
        
        tokens = response.json()
        access_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Start Game
        print("\nStarting Game...")
        game_data = {
            "game_mode": "flag_to_country",
            "regions": ["europe", "asia"],
            "questions_count": 5
        }
        response = await client.post(f"{BASE_URL}/games/start", json=game_data, headers=headers)
        if response.status_code == 200:
            game = response.json()
            game_id = game["id"]
            print(f"Game Started: {game_id}")
            print(f"Mode: {game['game_mode']}")
        else:
            print(f"Start Game failed: {response.status_code} {response.text}")
            sys.exit(1)
            
        # 3. Get Questions
        print("\nGetting Questions...")
        response = await client.get(f"{BASE_URL}/games/{game_id}/questions", headers=headers)
        if response.status_code == 200:
            questions = response.json()
            print(f"Received {len(questions)} questions")
            if len(questions) > 0:
                q1 = questions[0]
                print(f"Q1: {q1['text']}")
                print(f"Options: {[o['name'] for o in q1['options']]}")
        else:
            print(f"Get Questions failed: {response.status_code} {response.text}")
            sys.exit(1)
            
        # 4. End Game
        print("\nEnding Game...")
        result_data = {
            "score": 500,
            "correct_count": 5,
            "avg_response_ms": 1200,
            "max_streak": 5
        }
        response = await client.post(f"{BASE_URL}/games/{game_id}/end", json=result_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"Game Ended. Final Score: {result['score']}")
        else:
            print(f"End Game failed: {response.status_code} {response.text}")
            sys.exit(1)
            
        print("\nAll Game Tests Passed!")

if __name__ == "__main__":
    asyncio.run(test_game_flow())
