import os
import yaml
from modules.llm import GroqClient, GroqCompletion

class SummaryGenerator:
    def __init__(self, api_key, model, domain, prompt_template_file, user_content_file, prompt_key='summarize_text', temperature=0, max_tokens=8192, top_p=1, stream=True, stop=None, skip_chunking=False):
        # Initialize the class with parameters
        self.api_key = api_key
        self.model = model
        self.domain = domain
        self.prompt_template_file = prompt_template_file
        self.user_content_file = user_content_file
        self.prompt_key = prompt_key  # User-defined prompt key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stream = stream
        self.stop = stop
        self.skip_chunking = skip_chunking  # Flag to skip chunking and resummarizing

        # Read the prompt template from YAML file
        self.prompt_template = self._read_prompt_template()

        # Read the user content from the markdown file
        self.user_content = self._read_user_content()

    def _read_prompt_template(self):
        """Reads the user-defined prompt template from the YAML file."""
        with open(self.prompt_template_file, 'r') as file:
            yaml_content = yaml.safe_load(file)
            return yaml_content.get('prompts', {}).get(self.prompt_key, {}).get('template', '')

    def _read_user_content(self):
        """Reads the user content from the markdown file with correct encoding."""
        try:
            # Attempt to read the file with UTF-8 encoding
            with open(self.user_content_file, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Fallback to a more forgiving encoding
            with open(self.user_content_file, 'r', encoding='latin-1') as file:
                return file.read()

    def _line_count(self, text):
        """Returns the number of lines in the provided text."""
        return len(text.splitlines())

    def _split_into_chunks(self, text, max_length=15000):
        """Splits the text into chunks of a maximum length."""
        return [text[i:i + max_length] for i in range(0, len(text), max_length)]

    def _summarize_chunk(self, chunk):
        """Generates a summary for a single chunk of content."""
        # Initialize the GroqClient with the provided API key
        groq_client = GroqClient(self.api_key)

        # Create an instance of GroqCompletion with the specified parameters
        groq_completion = GroqCompletion(
            groq_client, 
            self.model, 
            self.domain, 
            self.prompt_template, 
            chunk, 
            self.temperature, 
            self.max_tokens, 
            self.top_p, 
            self.stream, 
            self.stop
        )

        # Generate the completion using the provided content
        return groq_completion.create_completion()

    def generate_summary(self):
        """Generates a summary for the user content."""
        if self.skip_chunking:
            # If skip_chunking flag is True, do not split or resummarize
            print("Skipping chunking and resummarizing...")
            result = self._summarize_chunk(self.user_content)

            # Write the summary back to the user content file
            with open(self.user_content_file, 'w') as file:
                file.write(result)

            return result
        else:
            # Check if the document exceeds 15000 characters and proceed with chunking
            if len(self.user_content) > 15000:
                print("Document exceeds 15000 characters, splitting into chunks...")

                # Split content into chunks of 15000 characters
                chunks = self._split_into_chunks(self.user_content)

                # Generate summaries for each chunk
                summaries = []
                for chunk in chunks:
                    result = self._summarize_chunk(chunk)
                    summaries.append(result)

                # Combine all the summaries into one
                combined_summary = '\n'.join(summaries)

                # Check if the combined summary exceeds 100 lines
                if self._line_count(combined_summary) > 100:
                    print("Combined summary exceeds 100 lines, summarizing again...")
                    # Generate the summary of the combined summary
                    return self._summarize_chunk(combined_summary)
                else:
                    # Write the combined summary back to the user content file
                    with open(self.user_content_file, 'w') as file:
                        file.write(combined_summary)

                    return combined_summary
            else:
                # If the document is smaller than 15000 characters, summarize it directly
                print("Document has 15000 characters or fewer, summarizing directly...")
                result = self._summarize_chunk(self.user_content)

                # Write the summary back to the user content file
                with open(self.user_content_file, 'w') as file:
                    file.write(result)

                return result

# Example usage:
# if __name__ == "__main__":
#     api_key = os.environ.get("GROQ_API_KEY")  # Get API key from environment variables
#     model = "gemma2-9b-it"  # Example model name
#     domain = ""  # You can provide a domain if needed
#     prompt_template_file = "prompts.yml"  # YAML file with the 'summarize_text' prompt template
#     user_content_file = "scrapPages/LLM_Instruction_1_Scrap_1.md"  # Markdown file containing user content
#     prompt_key = 'summarize_text'  # The prompt key defined by the user

#     # Create an instance of the SummaryGenerator class
#     summary_generator = SummaryGenerator(api_key, model, domain, prompt_template_file, user_content_file, prompt_key)

#     # Call the generate_summary method to get the result
#     result = summary_generator.generate_summary()

#     # Print the result (generated summary)
#     print(result)
