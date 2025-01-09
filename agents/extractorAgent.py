import os
import json
import yaml
from dotenv import load_dotenv
from agents.g2ReviewAgent import G2Scraper
from modules.llm import GroqClient, GroqCompletion
from agents.duckSearchAgent import DuckDuckGoSearch
from pydantic import BaseModel, ValidationError

load_dotenv()

class NameExtractorAgent:
    """
    A class to handle LLM processing with retry logic and validation.
    """

    def __init__(self, api_key, llm_model, prompts_file):
        self.groq_client = GroqClient(api_key)
        self.llm_model = llm_model
        self.prompts = self.load_prompts(prompts_file)

    @staticmethod
    def load_prompts(prompts_file):
        """Load prompts from a YAML file."""
        with open(prompts_file, 'r') as file:
            return yaml.safe_load(file)["prompts"]

    class ProductCompanyOutput(BaseModel):
        name: str
        domain: str

    def get_prompt_template(self, key):
        """Retrieve the prompt template by key."""
        return self.prompts[key]["template"]

    def call_llm(self, LLMmodel, domain, query, temperature, max_tokens, top_p, stream, stop, prompt_template):
        """Call the LLM and return the result."""
        groq_completion = GroqCompletion(
            self.groq_client,
            LLMmodel,
            domain,
            prompt_template,
            query,
            temperature,
            max_tokens,
            top_p,
            stream,
            stop
        )
        return groq_completion.create_completion()

    def process_request(self, LLMmodel, domain, query, temperature, max_tokens, top_p, stream, stop, prompt_key, max_attempts=3):
        """
        Process the LLM request with retries and validation.
        
        Parameters:
            LLMmodel: The model to use.
            domain: The domain context for the LLM.
            query: The query to process.
            temperature: Temperature setting for the LLM.
            max_tokens: Maximum tokens to generate.
            top_p: Top-p sampling parameter.
            stream: Whether to stream the results.
            stop: Stop sequence for the LLM.
            prompt_key: Key to retrieve the appropriate prompt template.
            max_attempts: Maximum number of retry attempts.
        
        Returns:
            Validated output JSON or None if validation fails after retries.
        """
        attempts = 0
        validated_output = None
        result_json = None
        prompt_template = self.get_prompt_template(prompt_key)

        while attempts < max_attempts:
            result = self.call_llm(LLMmodel, domain, query, temperature, max_tokens, top_p, stream, stop, prompt_template)

            try:
                result_json = json.loads(result)
                validated_output = self.ProductCompanyOutput(**result_json)
                break  # Exit the loop if validation is successful
            except (json.JSONDecodeError, ValidationError) as e:
                print(f"Error in processing the result on attempt {attempts + 1}:", e)

            attempts += 1

        if validated_output:
            return result_json
        else:
            print("Failed to get a valid output after 3 attempts.")
            return None

# # Initialize variables
# api_key = os.getenv("GROQ_API_KEY")

# llm_model = {"LLama3.3-70B": "llama-3.3-70b-versatile"}
# prompts_file = "prompts.yml"
# prompt_key = "identify_product_or_company"
# LLMmodel = llm_model['LLama3.3-70B']
# domain = ""
# query = "give me report of Samsung S24"
# temperature = 0.0
# max_tokens = 300
# top_p = 1
# stream = True
# stop = None

# processor = LLMProcessor(api_key, llm_model, prompts_file)
# result = processor.process_request(LLMmodel, domain, query, temperature, max_tokens, top_p, stream, stop, prompt_key)

# if result:
#     print("Validated Output JSON:", result)