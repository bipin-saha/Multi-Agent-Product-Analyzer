import json
import os
import asyncio
import time
from agents.duckSearchAgent import DuckDuckGoSearch
from agents.scrapperAgent import WebContentCleaner
from modules.llamSummarizer import SummaryGenerator

# Assuming necessary imports like DuckDuckGoSearch, WebContentCleaner, and SummaryGenerator are defined elsewhere

async def process_search_and_generate_summary(query, max_search, api_key, domain, prompts_file):
    # Perform DuckDuckGo search
    ddg_search = DuckDuckGoSearch(query, max_search)
    search_results = ddg_search.perform_search()
    search_results = json.loads(search_results)

    # Loop through each search result and perform WebContentCleaner asynchronously
    async def clean_and_generate_summary_for_result(idx, url):
        print(f"Cleaning content for URL: {url}")
        cleaner = WebContentCleaner(url=url, fit_markdown_path=os.path.join("scrapPages", f"LLM_Instruction_1_Scrap_{idx+1}.md"))
        await cleaner.clean_content()
        
        # Generate summary
        summary_generator = SummaryGenerator(api_key, "llama3-70b-8192", domain, prompts_file, os.path.join("scrapPages", f"LLM_Instruction_1_Scrap_{idx+1}.md", 'summarize_text'))
        summary_generator.generate_summary()

    # Clean and generate summary for all search results
    tasks = [clean_and_generate_summary_for_result(idx, result['link']) for idx, result in enumerate(search_results)]
    await asyncio.gather(*tasks)

    # Wait for a second after processing
    time.sleep(1)

# Function to initiate the process
def run_processing(query, max_search, api_key, domain, prompts_file):
    asyncio.run(process_search_and_generate_summary(query, max_search, api_key, domain, prompts_file))
