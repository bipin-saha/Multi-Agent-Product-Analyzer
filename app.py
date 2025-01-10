import os
import time
import json
import asyncio
import nest_asyncio
import streamlit as st
from pydantic import BaseModel, ValidationError
from agents.queryAnalyzerAgent import QueryAnalyzerAgent
from agents.duckSearchAgent import DuckDuckGoSearch
from agents.scrapperAgent import WebContentCleaner
from agents.g2ReviewAgent import G2Scraper
from modules.g2validator import g2validator
from modules.llamSummarizer import SummaryGenerator
from modules.textCombiner import FileReader

# Apply nest_asyncio for compatibility with Streamlit
nest_asyncio.apply()

# Fix asyncio issues on Windows by setting ProactorEventLoopPolicy
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Streamlit app setup
st.set_page_config(page_title="Multi Agent Product Analyzer", layout="wide")
st.markdown("<h2 style='text-align: center;'>Multi Agent Product Analyzer</h2>", unsafe_allow_html=True)

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
query = st.text_input("Enter your query")
# query = st.chat_input(key="input", placeholder="Ask your question")

if st.button("Run Analysis", type="primary"):
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.status("Analyzing query... and generating search recommendation", expanded=True) as status:
            processor = QueryAnalyzerAgent(api_key, llm_model, prompts_file)
            llm_result = processor.process_request(LLMmodel, domain, query, temperature, max_tokens, top_p, stream, stop, prompt_key)
            if llm_result:
                st.success(f"Name: {llm_result['name']}")
                st.toast(f"Search Recommendation: {llm_result['instruction_1']}")
                st.toast(f"Search Recommendation: {llm_result['instruction_2']}")
                status.update(label="Query analysis complete!", state="complete", expanded=False)
            else:
                st.error("Error processing the query. Please try again.")
        
    ## EXTRACTING G2 REVIEWS ###
    with col2:
        with st.status("Extracting Insights from G2", expanded=True) as status:
            query = llm_result['name'] + " G2"
            max_search = 3
            ddg_search = DuckDuckGoSearch(query, max_search)
            search_results = ddg_search.perform_search()
            g2valid = g2validator(json.loads(search_results))[0]
            st.toast(f"Fetching: {g2valid}")
            try:
                # st.write(f"Searching {llm_result['name']} in G2 Reviews")
                scraper = G2Scraper()
                product_url = g2valid
                # st.write("Product URL:", product_url)
                reviews = scraper.fetch_reviews(product_url)

                g2Result = {
                    "productName": reviews['body']['productName'], "productLink": reviews['body']['productLink'], 
                    "productDescription": reviews['body']['productDescription'], "starRating": reviews['body']['starRating'],
                    "reviewsCount": reviews['body']['reviewsCount'], "discussionsCount": reviews['body']['discussionsCount'],
                    "ratings": reviews['body']['ratings'], "sentiments": reviews['body']['sentiments']
                }

                with open(os.path.join('scrapPages', 'conciseG2.json'), 'w') as json_file:
                    json.dump(g2Result, json_file, indent=4)

                if g2Result:
                    status.update(label="Extracted G2 Reviews!", state="complete", expanded=True)
                else:
                    st.error("Error extracting G2 reviews.")
                # st.write("Extracted G2 Reviews of Product:", llm_result['name'])

            except Exception as e:
                st.error(f"Error: {e}")

            time.sleep(1)

    ### EXTRACTING CONTENT FROM 1ST INSTRUCTION ###
    with col3:
        with st.status(f"Searching {llm_result['instruction_1']}", expanded=True) as status:
            query = llm_result['instruction_1']
            max_search = 3
            ddg_search = DuckDuckGoSearch(query, max_search)
            search_results = ddg_search.perform_search()
            search_results = json.loads(search_results)

            async def clean_all_content():
                for idx, result in enumerate(search_results):
                    url = result['link']
                    st.toast(f"Enriching Knowledge Base from: {url}")
                    cleaner = WebContentCleaner(url=url, fit_markdown_path=os.path.join("scrapPages", f"LLM_Instruction_1_Scrap_{idx+1}.md"))
                    await cleaner.clean_content()
                    summary_generator = SummaryGenerator(api_key, "llama3-70b-8192", domain, prompts_file, os.path.join("scrapPages", f"LLM_Instruction_1_Scrap_{idx+1}.md"), 'summarize_text', skip_chunking=False)
                    summary_generator.generate_summary()

            try:
                asyncio.run(clean_all_content())
                status.update(label=f"Extracted {llm_result['instruction_1']}", state="complete", expanded=True)
            except Exception as e:
                st.error("Error in Web Search.")
            
            

            time.sleep(1)

    ### EXTRACTING CONTENT FROM 2ND INSTRUCTION ###
    with col3:
        with st.status(f"Searching {llm_result['instruction_2']}", expanded=True) as status:
            # st.write("Searching Results for", llm_result['instruction_2'])
            query = llm_result['instruction_2']
            max_search = 3
            ddg_search = DuckDuckGoSearch(query, max_search)
            search_results = ddg_search.perform_search()
            search_results = json.loads(search_results)
            # st.write("Search Result for Instruction 2:", search_results)

            async def clean_all_content_2():
                for idx, result in enumerate(search_results):
                    url = result['link']
                    st.toast(f"Enriching Knowledge Base from: {url}")
                    cleaner = WebContentCleaner(url=url, fit_markdown_path=os.path.join("scrapPages", f"LLM_Instruction_2_Scrap_{idx+1}.md"))
                    await cleaner.clean_content()
                    summary_generator = SummaryGenerator(api_key, "llama3-70b-8192", domain, prompts_file, os.path.join("scrapPages", f"LLM_Instruction_2_Scrap_{idx+1}.md"), 'summarize_text', skip_chunking=False)
                    summary_generator.generate_summary()

            try:
                asyncio.run(clean_all_content_2())
                status.update(label=f"Extracted {llm_result['instruction_2']}", state="complete", expanded=True)
            except Exception as e:
                st.error("Error in Web Search.")


    with col4:
        with st.status(f"Performing Analysis", expanded=True) as status:
            folder_path = "scrapPages"  # Replace with your folder path
            file_reader = FileReader(folder_path)
            all_text = file_reader.read_files()

            # Write the combined text to a .md file
            with open("scrapPages/combinedReport.md", "w") as md_file:
                md_file.write(all_text)

            # st.write("Combined Report:", all_text)

            final_result = SummaryGenerator(api_key, LLMmodel, domain, prompts_file, "scrapPages/combinedReport.md", "business_analysis", skip_chunking=True)
            x = final_result.generate_summary()
            
            if x:
                status.update(label=f"Output Generated", state="complete", expanded=True)
            else:
                st.error("Error in generating output.")
    
    if x:
        st.markdown(f"""
        <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 5px;">
            <h4>Generated Output:</h4>
            <p>{x}</p>
        </div>
        """, unsafe_allow_html=True)
