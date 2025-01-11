import os
from phi.agent import Agent
from phi.tools.googlesearch import GoogleSearch
from phi.model.groq import Groq

agent = Agent(
    model=Groq(id="llama-3.2-3b-preview", api_key=os.getenv("GROQ_API_KEY")),
    tools=[GoogleSearch()],
    description="You are a helpful AI agent that can find competitors for a product or a company.",
    instructions=[
        "Provide a list of 5 competitors for that product along with their owner company names as a list only."
    ],
    show_tool_calls=True,
    debug_mode=True,
)
agent.print_response("Skype", markdown=True)
