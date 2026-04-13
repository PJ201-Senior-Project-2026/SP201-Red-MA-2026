from google.adk.agents import LlmAgent
from serpapi import SerpApiClient # type: ignore
import os
from dotenv import load_dotenv
load_dotenv()

import agents.tools as tools


def search(query: str):
    """Search the web using DuckDuckGo via SerpApi."""
    client = SerpApiClient({
        "engine": "duckduckgo_light",
        "api_key": os.getenv("SERPAPI_KEY"),
        "q": query,
        "kl": "us-en"
    })
    return client.get_dict()


# Agent 1: Search
search_agent = LlmAgent(
    model='gemini-2.5-flash',
    name="SearchAgent",
    description="Searches for information and summarizes findings.",
    instruction="Access external data sources through authorized public APIs. Obtain pertinent textual information about the designated sub-questions. Provide organized search results with URLs and source titles. Utilize specified retry mechanisms to address API errors.",
    tools=[search]
)

# Agent 2: Synthesizer
synthesizer_agent = LlmAgent(
    model='gemini-2.5-flash',
    name="SynthesizerAgent",
    description="Synthesize searched information",
    instruction="Combine search results into a draft that is logically organized and cohesive. Keep the citation references for the sources you have retrieved. Create output that can be seen in the user interface in markdown format."
)

# Agent 3: Fact-Checker
fact_checker_agent = LlmAgent(
    model='gemini-2.5-flash',
    name="FactCheckerAgent",
    description="Fact check the information found from searched result",
    instruction="Compare the synthesized statements with the retrieved original content. Determine which allegations are unsubstantiated or unverifiable. Flag or reject drafts that are inconsistent. When required, initiate the re-execution of the Search or Synthesis phases."
)

# The Manager (Orchestrator)
root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name="ManagerAgent",
    instruction="""
    You are a Project Manager. Your goal is to orchestrate a team of agents to complete complex user requests.

    The user's research state is stored in session:
    - Username: {user_name}
    - Research History: {research_history}

    1. Accept a study prompt that was supplied by a user.
    2. Break down the prompt into at least three well-structured subquestions.
    3. Assign one or more instances of the Search Agent to each sub-question.
    4. Organize the flow of the workflow for each agent.
    5. If the Fact-Checker Agent rejects the manuscript, start the search or synthesis over.
    6. Return the final, approved output to the user after aggregating it.
    7. After delivering the final output, use the save_research tool to store the topic and results.
    8. Use the view_research_history tool when the user asks about past research.
    """,
    sub_agents=[search_agent, synthesizer_agent, fact_checker_agent],
    tools=[
        tools.save_research,
        tools.view_research_history,
    ],
)
