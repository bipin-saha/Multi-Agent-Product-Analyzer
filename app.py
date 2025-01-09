import os
import json
import yaml
from dotenv import load_dotenv
from agents.g2ReviewAgent import G2Scraper
from modules.llm import GroqClient, GroqCompletion
from modules.g2validator import g2validator
from agents.duckSearchAgent import DuckDuckGoSearch
from agents.extractorAgent import NameExtractorAgent
load_dotenv()


# Initialize variables
api_key = os.getenv("GROQ_API_KEY")

llm_model = {"LLama3.3-70B": "llama-3.3-70b-versatile"}
prompts_file = "prompts.yml"
prompt_key = "identify_product_or_company"
LLMmodel = llm_model['LLama3.3-70B']
domain = ""
query = "give me report of Deepgram"
temperature = 0.0
max_tokens = 300
top_p = 1
stream = True
stop = None

processor = NameExtractorAgent(api_key, llm_model, prompts_file)
result = processor.process_request(LLMmodel, domain, query, temperature, max_tokens, top_p, stream, stop, prompt_key)

if result:
    print("Validated Output JSON:", result['name'])
    search_query = (result['name']) + " G2"
    max_results = 5
    print("Search Query:", search_query)
    ddg_search = DuckDuckGoSearch(search_query, max_results)
    search_results_json = ddg_search.perform_search()
    print("Search Results:", search_results_json)
    g2validator_results = g2validator(json.loads(search_results_json))[0]
    print("G2 Validated Link:", g2validator_results)

    try:
        scraper = G2Scraper()
        product_url = g2validator_results
        reviews = scraper.fetch_reviews(product_url)

        result = {
        "productName": reviews['body']['productName'],
        "productLink": reviews['body']['productLink'],
        "productDescription": reviews['body']['productDescription'],	
        "starRating": reviews['body']['starRating'],
        "reviewsCount": reviews['body']['reviewsCount'],
        "discussionsCount": reviews['body']['discussionsCount'],
        "ratings": reviews['body']['ratings'],
        "sentiments": reviews['body']['sentiments']
    }

        # Save JSON response to a file
        with open('reviews.json', 'w') as json_file:
            json.dump(reviews, json_file, indent=4)

        with open('results.json', 'w') as json_file:
            json.dump(result, json_file, indent=4)

        # # Print formatted JSON
        # print(json.dumps(reviews, indent=4))
    except Exception as e:
        print(f"Error: {e}")

    groq_client = GroqClient(api_key)
    LLMmodel = llm_model['LLama3.3-70B']
    domain = ''
    prompt_template = """You are an AI assistant designed to do SWOT Analsysis based on company data. 
                        You will analyze the company data and provide a SWOT analysis based on the data.
                        """
        
    user_content = result
    temperature = 0.5
    max_tokens = 4096
    top_p = 1
    stream = True
    stop = None

    groq_completion = GroqCompletion(groq_client, LLMmodel, domain, prompt_template, user_content, temperature, max_tokens, top_p, stream, stop)
    result = groq_completion.create_completion()
    print(result)