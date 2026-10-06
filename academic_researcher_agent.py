from crewai import Agent

from research_tools import (
    OpenAlexSearchTool,
    CrossrefSearchTool,
    ArxivSearchTool,
)


def create_academic_researcher(llm):
    return Agent(
        role="Academic Research Specialist",
        goal=(
            "Find strong scholarly evidence related to the research "
            "question using academic databases and identify important "
            "papers, authors, publication years and DOIs."
        ),
        backstory=(
            "You are an academic research specialist. "
            "You distinguish scholarly evidence from casual web content "
            "and prioritize relevant research literature."
        ),
        tools=[
            OpenAlexSearchTool(),
            CrossrefSearchTool(),
            ArxivSearchTool(),
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
