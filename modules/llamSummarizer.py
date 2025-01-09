import os
import yaml
from modules.llm import GroqClient, GroqCompletion

class SummaryGenerator:
    def __init__(self, api_key, model, domain, prompt_template_file, user_content_file, temperature=0, max_tokens=8192, top_p=1, stream=True, stop=None):
        # Initialize the class with parameters
        self.api_key = api_key
        self.model = model
        self.domain = domain
        self.prompt_template_file = prompt_template_file
        self.user_content_file = user_content_file
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stream = stream
        self.stop = stop

        # Read the prompt template from YAML file
        self.prompt_template = self._read_prompt_template()

        # Read the user content from the markdown file
        self.user_content = self._read_user_content()

    def _read_prompt_template(self):
        """Reads the 'summarize_text' template from the YAML file."""
        with open(self.prompt_template_file, 'r') as file:
            yaml_content = yaml.safe_load(file)
            return yaml_content.get('prompts', {}).get('summarize_text', {}).get('template', '')

    def _read_user_content(self):
        """Reads the user content from the markdown file with correct encoding."""
        with open(self.user_content_file, 'r', encoding='utf-8') as file:
            return file.read()

    def generate_summary(self):
        """Generates a summary using the GroqClient and writes it back to the user content file."""
        # Initialize the GroqClient with the provided API key
        groq_client = GroqClient(self.api_key)

        # Create an instance of GroqCompletion with the specified parameters
        groq_completion = GroqCompletion(
            groq_client, 
            self.model, 
            self.domain, 
            self.prompt_template, 
            self.user_content, 
            self.temperature, 
            self.max_tokens, 
            self.top_p, 
            self.stream, 
            self.stop
        )

        # Generate the completion using the provided content
        result = groq_completion.create_completion()

        # Write the summary (result) back to the same file
        with open(self.user_content_file, 'w') as file:
            file.write(result)

        return result

# # Example usage:
# api_key = os.environ.get("GROQ_API_KEY")
# model = "gemma2-9b-it"
# domain = ""
# prompt_template_file = "prompts.yml"  # YAML file with the 'summarize_text' prompt template
# user_content_file = "scrapPages/LLM_Instruction_1_Scrap_1.md"  # Markdown file containing user content

# # Create an instance of the SummaryGenerator class
# summary_generator = SummaryGenerator(api_key, model, domain, prompt_template_file, user_content_file)

# # Call the generate_summary method to get the result
# result = summary_generator.generate_summary()
# print(result)
