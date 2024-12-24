import asyncio
import os
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to download the image and save it to a file with a custom name
async def download_image(image_url: str, save_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                with open(save_path, 'wb') as f:
                    f.write(await response.read())
                print(f"Image saved successfully as {save_path}!")
            else:
                print(f"Failed to download image. Status code: {response.status}")

# Function to generate and download multiple images with custom names
async def generate_and_download_images(num_images: int, folder_name: str, user_names: list):
    image_paths = []

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Set up Selenium with headless Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/bin/chromedriver") 
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://inspirobot.me/") # Here goes the website from where we are going to get our inspiration

    previous_image_url = None

    for i in range(num_images):
        # Click the "Generate" button to create a new meme
        generate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.btn-text'))
        )
        generate_button.click()
        await asyncio.sleep(4)
        # Wait until a new image is generated
        while True:
            try:
                generated_image = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.generated-image'))
                )
                image_url = generated_image.get_attribute('src')

                # Check if the new image URL is different from the previous one
                if image_url != previous_image_url:
                    previous_image_url = image_url
                    break  # Exit the loop once a new image is generated
                else:
                    await asyncio.sleep(1)  # Wait for another second and check again
            except Exception as e:
                print("Error finding generated image:", e)
                break

        # Use the user-specified names for the image files
        image_name = f'{user_names[i]}_image.png'
        image_save_path = os.path.join(folder_name, image_name)
        image_paths.append(image_save_path)

        # Download the image with the correct full path
        await download_image(image_url, image_save_path)

    driver.quit()
    return image_paths
