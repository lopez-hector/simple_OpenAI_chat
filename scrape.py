import requests
from bs4 import BeautifulSoup

def get_text_from_webpage(url):
  # Send a GET request to the webpage
  response = requests.get(url)

  # Parse the HTML content using BeautifulSoup
  soup = BeautifulSoup(response.content, 'html.parser')

  # Find all the text content in the webpage
  text_content = soup.get_text()

  return text_content

# Example usage
url = 'https://stable-diffusion-art.com/how-to-come-up-with-good-prompts-for-ai-image-generation/'  # Replace with the URL of the webpage you want to extract text from
webpage_text = get_text_from_webpage(url)
print(webpage_text.replace('\n', ''))