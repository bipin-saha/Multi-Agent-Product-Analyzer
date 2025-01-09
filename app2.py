import os
import time
import json
import asyncio
import nest_asyncio
from pydantic import BaseModel, ValidationError
from agents.queryAnalyzerAgent import QueryAnalyzerAgent
from agents.duckSearchAgent import DuckDuckGoSearch
from agents.scrapperAgent import WebContentCleaner
from agents.g2ReviewAgent import G2Scraper
from modules.g2validator import g2validator

nest_asyncio.apply()

# Initialize variables
api_key = os.getenv("GROQ_API_KEY")
llm_model = {"LLama3.3-70B": "llama-3.3-70b-versatile"}
prompts_file = "prompts.yml"
prompt_key = "identify_product_or_company"
LLMmodel = llm_model['LLama3.3-70B']
domain = ""
temperature = 0.0
max_tokens = 500
top_p = 1
stream = True
stop = None

# Initialize QueryAnalyzerAgent
processor = QueryAnalyzerAgent(api_key, llm_model, prompts_file)
query = """Analyze the competitive landscape for AI-based writing assistants targeting academic users. 
            Provide insights on market trends, feature gaps, pricing strategies, and suggest opportunities
            for differentiation, backed by customer reviews and funding data from Grammarly."""
result = processor.process_request(LLMmodel, domain, query, temperature, max_tokens, top_p, stream, stop, prompt_key)
print(result)

query = result['name'] + " G2"
max_results = 3
ddg_search = DuckDuckGoSearch(query, max_results)
search_results = ddg_search.perform_search()
g2valid = g2validator(json.loads(search_results))[0]

try:
        scraper = G2Scraper()
        product_url = g2valid
        reviews = scraper.fetch_reviews(product_url)

        result = {
        "productName": reviews['body']['productName'], "productLink": reviews['body']['productLink'], 
        "productDescription": reviews['body']['productDescription'], "starRating": reviews['body']['starRating'],
        "reviewsCount": reviews['body']['reviewsCount'], "discussionsCount": reviews['body']['discussionsCount'],
        "ratings": reviews['body']['ratings'], "sentiments": reviews['body']['sentiments']
    }

        with open(os.path.join('scrapPages', 'conciseG2.json'), 'w') as json_file:
            json.dump(result, json_file, indent=4)

except Exception as e:
    print(f"Error: {e}")

time.sleep(1)

query = result['instruction_1']
max_results = 3
ddg_search = DuckDuckGoSearch(query, max_results)
search_results = ddg_search.perform_search()
print("INSTRUCTION 1:", search_results)

time.sleep(1)

query = result['instruction_2']
max_results = 3
ddg_search = DuckDuckGoSearch(query, max_results)
search_results = ddg_search.perform_search()
print("INSTRUCTION 2:", search_results)


# Example usage: User provides file path for fit markdown
search_results = json.loads(search_results)
url = search_results[0]['link']
print("THE URL IS:", url)
cleaner = WebContentCleaner(url=url, fit_markdown_path="INTT_output.md")
asyncio.run(cleaner.clean_content())