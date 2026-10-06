from crewai import Agent

from research_tools import WebpageFetchTool


def create_evidence_agent(llm):
    return Agent(
        role="Evidence Verification Analyst",
        goal=(
            "Evaluate the research collected by the other researchers, "
            "identify unsupported claims, contradictions and weak evidence, "
            "and determine which findings are sufficiently supported."
        ),
        backstory=(
            "You are a skeptical evidence analyst. "
            "You do not accept claims simply because another researcher "
            "reported them. You inspect sources and clearly identify "
            "uncertainty."
        ),
        tools=[
            WebpageFetchTool(),
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
