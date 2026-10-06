from crewai import Crew, Process

from planner_agent import create_planner
from web_researcher_agent import create_web_researcher
from academic_researcher_agent import create_academic_researcher
from evidence_agent import create_evidence_agent
from writer_agent import create_writer

from tasks import create_tasks


AGENT_STAGES = [
    "Research Planner",
    "Web Researcher",
    "Academic Researcher",
    "Evidence Analyst",
    "Research Writer",
]


def create_research_crew(llm):
    planner = create_planner(llm)
    web_researcher = create_web_researcher(llm)
    academic_researcher = create_academic_researcher(llm)
    evidence_agent = create_evidence_agent(llm)
    writer = create_writer(llm)

    tasks = create_tasks(
        planner=planner,
        web_researcher=web_researcher,
        academic_researcher=academic_researcher,
        evidence_agent=evidence_agent,
        writer=writer,
    )

    crew = Crew(
        agents=[
            planner,
            web_researcher,
            academic_researcher,
            evidence_agent,
            writer,
        ],
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
    )

    return crew
