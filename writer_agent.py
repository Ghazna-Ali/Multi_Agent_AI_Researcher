from crewai import Agent

from research_tools import WebpageFetchTool


def create_writer(llm):
    return Agent(
        role="Research Report Writer",
        goal=(
            "Transform the verified research into a clear, accurate, "
            "well-structured final research report with transparent "
            "source references."
        ),
        backstory=(
            "You are an expert research writer. "
            "You synthesize evidence instead of simply repeating it. "
            "You distinguish established findings, emerging evidence "
            "and uncertainty."
        ),
        tools=[
            WebpageFetchTool(),
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
