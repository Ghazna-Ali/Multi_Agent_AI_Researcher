from crewai import Task


def create_tasks(
    planner,
    web_researcher,
    academic_researcher,
    evidence_agent,
    writer,
):
    # ============================================================
    # TASK 1: RESEARCH PLANNING
    # ============================================================

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

        - Main research objective
        - Key research questions
        - Important concepts
        - Web research directions
        - Academic research directions
        - Potential evidence risks
        """,
        agent=planner,
    )

    # ============================================================
    # TASK 2: WEB RESEARCH
    # ============================================================

    web_task = Task(
        description="""
        Conduct web research for the research question:

        {research_question}

        Use the research plan provided through your task context.

        Use your available research tools to find current and
        relevant information.

        You MUST:

        - Search for relevant information.
        - Inspect important sources.
        - Record source names.
        - Record source URLs.
        - Distinguish facts from opinions.
        - Avoid unsupported claims.
        - Prefer authoritative and recent sources.

        Produce a source-oriented web research report.
        """,
        expected_output="""
        A web research report containing:

        - Major findings
        - Supporting evidence
        - Current developments
        - Important sources
        - Source URLs
        - Areas of uncertainty
        """,
        agent=web_researcher,
        context=[planning_task],
    )

    # ============================================================
    # TASK 3: ACADEMIC RESEARCH
    # ============================================================

    academic_task = Task(
        description="""
        Conduct academic research for:

        {research_question}

        Use the research plan provided through your task context.

        You MUST use your academic research tools.

        Search relevant academic literature using:

        - OpenAlex
        - Crossref
        - arXiv

        Identify:

        - Relevant papers
        - Authors
        - Publication years
        - DOI information
        - Important findings
        - Research limitations where available

        Do not invent papers, authors, findings or citations.
        """,
        expected_output="""
        An academic research report containing:

        - Important papers
        - Authors
        - Publication years
        - DOI information
        - Main findings
        - Research limitations
        - Relevant URLs where available
        """,
        agent=academic_researcher,
        context=[planning_task],
    )

    # ============================================================
    # TASK 4: EVIDENCE ANALYSIS
    # ============================================================

    evidence_task = Task(
        description="""
        Act as the evidence verification layer.

        Research question:

        {research_question}

        Review the research outputs provided through your task context.

        Carefully evaluate the collected evidence.

        Identify:

        1. Strongly supported findings.
        2. Findings supported by multiple independent sources.
        3. Claims that require caution.
        4. Contradictions between sources.
        5. Missing evidence.
        6. Weak or unreliable sources.
        7. Areas where the evidence is still uncertain.

        Use the webpage fetch tool when source inspection is necessary.

        Do not create new unsupported facts.

        Your job is to challenge the research rather than simply
        accepting everything the previous agents reported.
        """,
        expected_output="""
        An evidence assessment containing:

        - Verified findings
        - Strong evidence
        - Multiple-source evidence
        - Conflicting evidence
        - Weak or unsupported claims
        - Missing evidence
        - Important uncertainties
        - Recommendations for the final writer
        """,
        agent=evidence_agent,
        context=[
            planning_task,
            web_task,
            academic_task,
        ],
    )

    # ============================================================
    # TASK 5: FINAL RESEARCH REPORT
    # ============================================================

    writing_task = Task(
        description="""
        Produce the final research report for:

        {research_question}

        Use all research and evidence-analysis outputs provided
        through your task context.

        Synthesize the evidence rather than simply repeating
        individual researchers.

        Before finalizing:

        - Check important source URLs.
        - Do not invent citations.
        - Do not invent URLs.
        - Do not present uncertain claims as established facts.
        - Prefer findings supported by multiple sources.
        - Clearly distinguish academic evidence from general web sources.
        - Clearly identify conflicting evidence.
        - Clearly identify limitations.

        Write a professional, readable research report.
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

        The Sources section must contain the actual URLs
        discovered during the research process.
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
