from crewai import Agent

from research_tools import NewsSearchTool, WikipediaSearchTool


def create_planner(llm):
    return Agent(
        role="Research Planning Specialist",
        goal=(
            "Understand the research question and create a focused "
            "research plan that identifies the most important areas "
            "that must be investigated."
        ),
        backstory=(
            "You are an experienced research strategist. "
            "You turn broad research questions into clear, "
            "evidence-oriented research directions."
        ),
        tools=[
            NewsSearchTool(),
            WikipediaSearchTool(),
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
