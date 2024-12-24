import httpx
import random
import asyncio


class MemeManager:
    def __init__(self):
        self.memes = []  # Store memes here

    async def fetch_memes(self, count=3):
        """Fetch memes from the API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://meme-api.com/gimme/{count}')  # Fetch multiple memes
            data = response.json()
            # print(data)  # Print the data for debugging

            # Check if the response contains memes
            if 'memes' in data:
                self.memes = data['memes']  # Store the entire list of memes
            else:
                print("No 'memes' key found in response.")
                self.memes = []

    def get_random_meme(self):
        """Return a random meme URL."""
        if not self.memes:
            return None  # Return None if there are no memes loaded
        return random.choice(self.memes)  # Randomly choose a meme

    def preload_memes(self, count=3):
        """Fetch memes and store them synchronously."""
        asyncio.run(self.fetch_memes(count))  # Run the async fetch in a synchronous manner


meme_manager = MemeManager()
