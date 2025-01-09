import os
import time
import json
import asyncio
import nest_asyncio
from chatMode import chat_response
from pydantic import BaseModel, ValidationError
from agents.queryAnalyzerAgent import QueryAnalyzerAgent
from agents.duckSearchAgent import DuckDuckGoSearch
from agents.scrapperAgent import WebContentCleaner
from agents.g2ReviewAgent import G2Scraper
from modules.g2validator import g2validator
from modules.llamSummarizer import SummaryGenerator
from modules.textCombiner import FileReader

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

### INSTRUCTION ANALYSIS ###

# q_input = st.chat_input(key="input", placeholder="Ask your question")
query = """Analyze the competitive landscape for AI-powered productivity and writing tools targeting academic users.
            Provide insights on market trends, feature gaps, pricing strategies, and suggest opportunities
            for differentiation, backed by customer reviews and funding data from Notion."""
# query = q_input

# if q_input:
processor = QueryAnalyzerAgent(api_key, llm_model, prompts_file)
llm_result = processor.process_request(LLMmodel, domain, query, temperature, max_tokens, top_p, stream, stop, prompt_key)
print(llm_result)

### EXTRACTING G2 REVIEWS ###


query = llm_result['name'] + " G2"
max_search = 3
ddg_search = DuckDuckGoSearch(query, max_search)
search_results = ddg_search.perform_search()
g2valid = g2validator(json.loads(search_results))[0]

try:
        scraper = G2Scraper()
        product_url = g2valid
        print("Product URL:", product_url)
        reviews = scraper.fetch_reviews(product_url)

        g2Result = {
        "productName": reviews['body']['productName'], "productLink": reviews['body']['productLink'], 
        "productDescription": reviews['body']['productDescription'], "starRating": reviews['body']['starRating'],
        "reviewsCount": reviews['body']['reviewsCount'], "discussionsCount": reviews['body']['discussionsCount'],
        "ratings": reviews['body']['ratings'], "sentiments": reviews['body']['sentiments']
    }

        with open(os.path.join('scrapPages', 'conciseG2.json'), 'w') as json_file:
            json.dump(g2Result, json_file, indent=4)

except Exception as e:
    print(f"Error: {e}")

time.sleep(1)

### EXTRACTING CONTENT FROM 1ST INSTRUCTION ###

query = llm_result['instruction_1']
max_search = 3
ddg_search = DuckDuckGoSearch(query, max_search)
search_results = ddg_search.perform_search()
search_results = json.loads(search_results)
# Loop through each search result and perform WebContentCleaner asynchronously
async def clean_all_content():
    for idx, result in enumerate(search_results):
        url = result['link']
        print(f"Cleaning content for URL: {url}")
        cleaner = WebContentCleaner(url=url, fit_markdown_path=os.path.join("scrapPages", f"LLM_Instruction_1_Scrap_{idx+1}.md"))
        await cleaner.clean_content()
        # summary_generator = SummaryGenerator(api_key, "llama3-70b-8192", domain, prompts_file, os.path.join("scrapPages", f"LLM_Instruction_1_Scrap_{idx+1}.md"))
        summary_generator = SummaryGenerator(api_key, "llama3-70b-8192", domain, prompts_file, os.path.join("scrapPages", f"LLM_Instruction_1_Scrap_{idx+1}.md"), 'summarize_text', skip_chunking=False)
        summary_generator.generate_summary()

asyncio.run(clean_all_content())

time.sleep(1)


### EXTRACTING CONTENT FROM 2ND INSTRUCTION ###


query = llm_result['instruction_2']
max_search = 3
ddg_search = DuckDuckGoSearch(query, max_search)
search_results = ddg_search.perform_search()
search_results = json.loads(search_results)
print("Search Result for Instruction 2:", search_results)

# Loop through each search result and perform WebContentCleaner asynchronously
async def clean_all_content_2():
    for idx, result in enumerate(search_results):
        url = result['link']
        print(f"Cleaning content for URL: {url}")
        cleaner = WebContentCleaner(url=url, fit_markdown_path=os.path.join("scrapPages", f"LLM_Instruction_2_Scrap_{idx+1}.md"))
        await cleaner.clean_content()
        # summary_generator = SummaryGenerator(api_key, "llama3-70b-8192", domain, prompts_file, os.path.join("scrapPages", f"LLM_Instruction_2_Scrap_{idx+1}.md"))
        summary_generator = SummaryGenerator(api_key, "llama3-70b-8192", domain, prompts_file, os.path.join("scrapPages", f"LLM_Instruction_2_Scrap_{idx+1}.md"), 'summarize_text', skip_chunking=False)
        summary_generator.generate_summary()

# Run the asynchronous function for instruction 2
asyncio.run(clean_all_content_2())

folder_path = "scrapPages"  # Replace with your folder path
file_reader = FileReader(folder_path)
all_text = file_reader.read_files()

# Write the combined text to a .md file
with open("scrapPages/combinedReport.md", "w") as md_file:
    md_file.write(all_text)

# print("This is the combined Text:", all_text)

final_result = SummaryGenerator(api_key, LLMmodel, domain, prompts_file, "scrapPages/combinedReport.md", "business_analysis", skip_chunking=True)
x = final_result.generate_summary()
print("THE FINAL OUTPUT:", x)