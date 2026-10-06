from crewai import Agent

from research_tools import (
    NewsSearchTool,
    WikipediaSearchTool,
    WebpageFetchTool,
)


def create_web_researcher(llm):
    return Agent(
        role="Web Research Specialist",
        goal=(
            "Find current, relevant and trustworthy web information "
            "related to the research question. Inspect important "
            "sources rather than relying only on search snippets."
        ),
        backstory=(
            "You are a careful web researcher who gathers current "
            "information, identifies useful sources and records URLs "
            "so that claims can later be verified."
        ),
        tools=[
            NewsSearchTool(),
            WikipediaSearchTool(),
            WebpageFetchTool(),
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
