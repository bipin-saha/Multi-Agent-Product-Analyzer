import os
import yaml
from modules.llamSummarizer import SummaryGenerator

# Example usage:
api_key = os.environ.get("GROQ_API_KEY")
model = "gemma2-9b-it"
domain = ""
prompt_template_file = "prompts.yml"  # YAML file with the 'summarize_text' prompt template
user_content_file = "scrapPages/LLM_Instruction_1_Scrap_1.md"  # Markdown file containing user content

# Create an instance of the SummaryGenerator class
summary_generator = SummaryGenerator(api_key, model, domain, prompt_template_file, user_content_file)

# Call the generate_summary method to get the result
result = summary_generator.generate_summary()
print(result)