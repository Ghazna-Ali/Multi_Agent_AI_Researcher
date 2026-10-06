from crewai import Task


def create_tasks(
    planner,
    web_researcher,
    academic_researcher,
    evidence_agent,
    writer,
):
    planning_task = Task(
        description="""
        Analyze the following research question:

        {research_question}

        Create a focused research plan.

        Identify:
        1. The major questions that need investigation.
        2. Important concepts and terminology.
        3. What current information should be searched.
        4. What academic evidence should be searched.
        5. Potential disagreements or risks of misinformation.

        Use your research discovery tools before finalizing the plan.
        """,
        expected_output="""
        A structured research plan containing:
        - Main research objectives
        - Key subquestions
        - Important concepts
        - Web research directions
        - Academic research directions
        - Potential evidence risks
        """,
        agent=planner,
    )

    web_task = Task(
        description="""
        Research the question below using the research plan produced
        by the planner.

        Research question:
        {research_question}

        Research plan:
        {planning_task}

        Use your tools to find current and relevant web information.

        You MUST:
        - search for relevant information
        - inspect important sources
        - record source URLs
        - distinguish facts from opinions
        - avoid unsupported claims

        Return a source-oriented research report.
        """,
        expected_output="""
        Web research containing:
        - Major findings
        - Supporting evidence
        - Important current developments
        - Source names
        - Source URLs
        - Areas of uncertainty
        """,
        agent=web_researcher,
        context=[planning_task],
    )

    academic_task = Task(
        description="""
        Conduct academic research for:

        {research_question}

        Research plan:
        {planning_task}

        Search OpenAlex, Crossref and arXiv.

        You MUST use your academic research tools.

        Identify:
        - relevant papers
        - publication years
        - authors
        - DOI information
        - important findings
        - limitations where available

        Do not invent papers or citations.
        """,
        expected_output="""
        Academic research report containing:
        - Important papers
        - Authors
        - Years
        - DOI links
        - Main findings
        - Research limitations
        """,
        agent=academic_researcher,
        context=[planning_task],
    )

    evidence_task = Task(
        description="""
        Act as the evidence verification layer.

        Research question:
        {research_question}

        Review:

        PLANNING:
        {planning_task}

        WEB RESEARCH:
        {web_task}

        ACADEMIC RESEARCH:
        {academic_task}

        Identify:
        1. Strongly supported findings.
        2. Findings supported by multiple sources.
        3. Claims that require caution.
        4. Contradictions.
        5. Missing evidence.
        6. Sources that appear weak or unreliable.

        Use the webpage fetch tool when source inspection is necessary.

        Do not create new unsupported facts.
        """,
        expected_output="""
        Evidence assessment containing:
        - Verified findings
        - Strong evidence
        - Conflicting evidence
        - Weak or unsupported claims
        - Missing evidence
        - Recommendations for the final writer
        """,
        agent=evidence_agent,
        context=[
            planning_task,
            web_task,
            academic_task,
        ],
    )

    writing_task = Task(
        description="""
        Produce the final research report.

        Research question:
        {research_question}

        Use the following material:

        RESEARCH PLAN:
        {planning_task}

        WEB RESEARCH:
        {web_task}

        ACADEMIC RESEARCH:
        {academic_task}

        EVIDENCE REVIEW:
        {evidence_task}

        Write a professional research report.

        Before finalizing, use your source-inspection tool where useful.

        Rules:
        - Do not invent citations.
        - Do not invent URLs.
        - Do not present uncertain claims as established facts.
        - Prefer evidence supported by multiple sources.
        - Keep academic references clearly identifiable.
        - Include source URLs.
        """,
        expected_output="""
        A polished research report containing:

        # Executive Summary

        # Key Findings

        # Detailed Analysis

        # Academic Evidence

        # Conflicting or Uncertain Evidence

        # Conclusion

        # Sources

        The Sources section must include the URLs supplied by the
        research process.
        """,
        agent=writer,
        context=[
            planning_task,
            web_task,
            academic_task,
            evidence_task,
        ],
    )

    return [
        planning_task,
        web_task,
        academic_task,
        evidence_task,
        writing_task,
    ]
