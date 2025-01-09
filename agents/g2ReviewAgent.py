import os
from urllib.parse import quote_plus
from urllib.request import urlopen
import json
import time

class G2Scraper:
    """
    A class to scrape product reviews from G2 using the Crawlbase API.
    
    Attributes:
        api_token (str): The API token for accessing the Crawlbase API.
    """

    def __init__(self):
        """
        Initializes the G2Scraper class by loading the API token from environment variables.
        """
        self.api_token = os.getenv('CRAWLBASE_API_KEY')
        if not self.api_token:
            raise ValueError("API token not found. Please set the 'CRAWLBASE_API_TOKEN' environment variable.")

    def fetch_reviews(self, product_url: str) -> dict:
        """
        Fetches reviews for the given product URL from G2 with retry mechanism.

        Args:
            product_url (str): The G2 product reviews page URL.

        Returns:
            dict: Parsed JSON response containing product reviews.
        """
        encoded_url = quote_plus(product_url)
        api_url = (f'https://api.crawlbase.com/?token={self.api_token}&format=json&pretty=true'
                   f'&scraper=g2-product-reviews&url={encoded_url}')
        
        retries = 3
        for attempt in range(retries):
            try:
                with urlopen(api_url) as handler:
                    if handler.status != 200:
                        raise RuntimeError(f"Request failed with status code {handler.status}")
                    response_data = handler.read()
                return json.loads(response_data)

            except Exception as e:
                if attempt < retries - 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(2)  # Wait before retrying
                else:
                    raise RuntimeError(f"Failed to fetch reviews after {retries} attempts: {e}")

# if __name__ == "__main__":
#     # Example usage
#     try:
#         scraper = G2Scraper()
#         product_url = 'https://www.g2.com/products/ringex/reviews'
#         reviews = scraper.fetch_reviews(product_url)

#         result = {
#             "productName": reviews['body']['productName'],
#             "productLink": reviews['body']['productLink'],
#             "productDescription": reviews['body']['productDescription'],    
#             "starRating": reviews['body']['starRating'],
#             "reviewsCount": reviews['body']['reviewsCount'],
#             "discussionsCount": reviews['body']['discussionsCount'],
#             "ratings": reviews['body']['ratings'],
#             "sentiments": reviews['body']['sentiments']
#         }

#         # Output the result
#         print(json.dumps(result, indent=4))

#         # Save JSON response to a file
#         with open('reviews.json', 'w') as json_file:
#             json.dump(reviews, json_file, indent=4)

#         with open('results.json', 'w') as json_file:
#             json.dump(result, json_file, indent=4)

#     except Exception as e:
#         print(f"Error: {e}")
