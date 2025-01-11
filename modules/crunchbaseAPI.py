from crawlbase import CrawlingAPI
from bs4 import BeautifulSoup

def crawl(page_url, api_token):
 # Initialize the CrawlingAPI object with your token
 api = CrawlingAPI({'token': api_token})

 # Get the page content
 response = api.get(page_url)

 # Check if the request was successful
 if response['status_code'] == 200:
  # Scraped data
  scraped_data = scrape_data(response)

  print(f'{scraped_data}')
 else:
  print(f"Error: {response}")

def scrape_data(response):
 try:
  # Parse the HTML content using Beautiful Soup
  soup = BeautifulSoup(response['body'], 'html.parser')

  # Extract the title of the Crunchbase page
  title = soup.find('h1', class_='profile-name').get_text(strip=True)

  # Extract the description of the Crunchbase page
  description = soup.find('span', class_='description').get_text(strip=True)

  # Extract the location of the Crunchbase page
  location = soup.select_one('.section-content-wrapper li.ng-star-inserted').text.strip()

  # Extract the employees of the Crunchbase page
  employees = soup.select_one('.section-content-wrapper li.ng-star-inserted:nth-of-type(2)').text.strip()

  # Extract the Company URL of the Crunchbase page
  company_url = soup.select_one('.section-content-wrapper li.ng-star-inserted:nth-of-type(5) a[role="link"]')['href']

  # Extract the Rank of the Crunchbase page
  rank = soup.select_one('.section-content-wrapper li.ng-star-inserted:nth-of-type(6) span').text.strip()

  # Extract the Founded Date of the Crunchbase page
  founded = soup.select_one('.mat-mdc-card.mdc-card .text_and_value li:nth-of-type(4) field-formatter').text.strip()

  # Extract the Founders of the Crunchbase page
  founders = soup.select_one('.mat-mdc-card.mdc-card .text_and_value li:nth-of-type(5) field-formatter').text.strip()

  return {
   'title': title,
   'description': description,
   'location': location,
   'employees': employees,
   'company_url': company_url,
   'rank': rank,
   'founded': founded,
   'founders': founders,
  }
 except Exception as e:
  print(f"An error occurred: {e}")
  return {}

# if __name__ == "__main__":
#  # Specify the Crunchbase page URL to scrape
#  page_url = 'https://www.crunchbase.com/organization/zepto-29b1'

#  # Specify your Crawlbase token. Use the JavaScript token for Crunchbase
#  api_token = 'Crawlbase_Token'

#  # Call the crawl function
#  crawl(page_url, "API Key")