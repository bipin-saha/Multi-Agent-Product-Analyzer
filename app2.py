import os
import yaml
from modules.llm import GroqClient, GroqCompletion

def generate_summary(api_key, model, domain, prompt_template_file, user_content_file, temperature=0, max_tokens=8192, top_p=1, stream=True, stop=None):
    # Read the prompt_template from the YAML file
    with open(prompt_template_file, 'r') as file:
        yaml_content = yaml.safe_load(file)
        prompt_template = yaml_content.get('prompts', {}).get('summarize_text', {}).get('template', '')

    # Read the user content from the markdown file
    with open(user_content_file, 'r') as file:
        user_content = file.read()

    # Initialize the GroqClient with the provided API key
    groq_client = GroqClient(api_key)

    # Create an instance of GroqCompletion with the specified parameters
    groq_completion = GroqCompletion(
        groq_client, 
        model, 
        domain, 
        prompt_template, 
        user_content, 
        temperature, 
        max_tokens, 
        top_p, 
        stream, 
        stop
    )

    # Generate the completion using the provided content
    result = groq_completion.create_completion()

    # Write the summary (result) back to the same file
    with open(user_content_file, 'w') as file:
        file.write(result)

    return result

# Example usage:
api_key = os.environ.get("GROQ_API_KEY")
model = "gemma2-9b-it"
domain = ""
prompt_template_file = "prompts.yml"  # YAML file with the 'summarize_text' prompt template
user_content_file = "scrapPages/LLM_Instruction_1_Scrap_1.md"  # Markdown file containing user content

# Call the function
result = generate_summary(api_key, model, domain, prompt_template_file, user_content_file)
print(result)
