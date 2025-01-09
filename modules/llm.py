import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class GroqClient:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)  # Review this instantiation

class GroqCompletion:
    def __init__(self, client, model, domain, prompt_template, user_content, temperature, max_tokens, top_p, stream, stop):
        self.client = client
        self.model = model
        self.domain = domain
        self.prompt_template = prompt_template
        self.user_content = user_content
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stream = stream
        self.stop = stop

    def create_completion(self):
        prompt = f"{self.prompt_template}\n\n{self.user_content}\n"
        system_role = f"you are an helpful AI assistant in text based question answering and analyzing given business data."

        completion = self.client.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_role
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            stream=self.stream,
            stop=self.stop,
        )

        result = ""
        for chunk in completion:
            result += chunk.choices[0].delta.content or ""

        return result
    


# # Example usage
# api_key = os.environ.get("GROQ_API_KEY")
# groq_client = GroqClient(api_key)

# model = "gemma2-9b-it"
# domain = "LLM"
# prompt_template = "Summarize me this content in just one line"
# user_content = """1. **Domain Adaptation and Inference**: He developed a novel semantic encoding and decoding (SEDO) algorithm that uses knowledge graphs to generate semantic labels for unlabeled data. He applied this algorithm to detect suicide risk on social media.
# 2. **Weighted Constraints Conditioned on Time-Evolving Events**: He developed a semi-deep infusion-based framework that integrates real-world knowledge as weighted constraints conditioned upon time-evolving events. He applied this framework to estimate the rise in infection rate during a crisis event.      
# 3. **Matching and Ranking**: He developed a semi-deep K-IL system that models a patient's trust of GPs using knowledge of consultation history and ICD-10 graphs. He also applied this system to recommend patients to GPs."""
# temperature = 0
# max_tokens = 8192
# top_p = 1
# stream = True
# stop = None

# groq_completion = GroqCompletion(groq_client, model, domain, prompt_template, user_content, temperature, max_tokens, top_p, stream, stop)
# result = groq_completion.create_completion()
# print(result)