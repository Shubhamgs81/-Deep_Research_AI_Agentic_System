import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from typing import Dict, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize the LLM (using OpenAI as an example, replace with your preferred model)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize Tavily client for web search
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Define the shared state for the agents
class ResearchState(TypedDict):
    query: str
    research_data: List[Dict]
    final_answer: str

# Research Agent: Crawls the web and gathers information
def research_agent(state: ResearchState) -> ResearchState:
    query = state["query"]
    print(f"Research Agent: Searching for '{query}'...")

    # Use Tavily to search the web
    search_results = tavily_client.search(query, max_results=5)

    # Extract relevant information from search results
    research_data = []
    for result in search_results["results"]:
        research_data.append({
            "title": result["title"],
            "url": result["url"],
            "content": result["content"][:500]  # Limit content length for brevity
        })

    print(f"Research Agent: Found {len(research_data)} relevant sources.")
    return {"research_data": research_data}

# Answer Drafter Agent: Processes research data and drafts a response
def answer_drafter_agent(state: ResearchState) -> ResearchState:
    research_data = state["research_data"]
    query = state["query"]

    # Create a prompt for the answer drafter
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert at drafting concise and accurate answers. Based on the following research data, provide a clear and informative response to the query: "{query}".

        Research Data:
        {research_data}

        Provide a well-structured answer in 3-5 sentences, citing the sources where relevant.
        """
    )

    # Format the research data for the prompt
    research_text = "\n".join([f"- {item['title']}: {item['content']} (Source: {item['url']})" for item in research_data])
    chain = prompt | llm

    # Generate the final answer
    response = chain.invoke({"query": query, "research_data": research_text})
    final_answer = response.content

    print("Answer Drafter Agent: Drafted the final answer.")
    return {"final_answer": final_answer}

# Define the LangGraph workflow
def create_workflow():
    workflow = StateGraph(ResearchState)

    # Add nodes for each agent
    workflow.add_node("research_agent", research_agent)
    workflow.add_node("answer_drafter_agent", answer_drafter_agent)

    # Define the flow: Research Agent -> Answer Drafter Agent -> End
    workflow.add_edge("research_agent", "answer_drafter_agent")
    workflow.add_edge("answer_drafter_agent", END)

    # Set the entry point
    workflow.set_entry_point("research_agent")

    return workflow.compile()

# Main function to run the system
def run_deep_research_system(query: str) -> str:
    # Initialize the workflow
    app = create_workflow()

    # Initial state
    initial_state = {
        "query": query,
        "research_data": [],
        "final_answer": ""
    }

    # Run the workflow
    final_state = app.invoke(initial_state)

    return final_state["final_answer"]

# Example usage
if __name__ == "__main__":
    query = "What are the latest advancements in quantum computing?"
    answer = run_deep_research_system(query)
    print("\nFinal Answer:")
    print(answer)