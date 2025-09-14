from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from plc_config import PLCConfig

def make_language_agent():
    """Create language normalization agent for ABB PLC."""
    return Agent(
        name="ABB Language Normalizer",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "Identify the input language. If not English, translate requirements into precise technical English, aligning with terminology used in ABB PLC documentation.",
            "Return only the English version, omitting all translations.",
            "Preserve technical specifics, variable/data type conventions, and process details."
        ],
        markdown=False,
    )

def make_clarification_agent():
    """Create requirements clarification agent for ABB PLC."""
    return Agent(
        name="ABB PLC Requirements Clarifier",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "You are an ABB PLC automation expert for AC500/AC800 series.",
            "If input is complete, respond: CLEAR_INPUT",
            "Otherwise, ask ONE technical clarification about process specs, signals, or safety.",
            "If input is unclear, request specific ABB system details needed."
        ],
        markdown=True,
    )



def make_enhanced_code_agent():
    """Generate IEC 61131-3 Structured Text for ABB PLCs."""
    return Agent(
        name="ABB IEC 61131-3 Code Generator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        tools=[DuckDuckGo(search=True)],
        instructions=[
            "Generate ABB AC500/800 Structured Text code per IEC 61131-3 standards.",
            "Include VAR blocks, ABB naming conventions, safety interlocks.",
            "Return only ST code in fenced blocks with inline comments."
        ],
        markdown=True,
    )



def make_enhanced_flow_agent():
    """Generate ABB PLC logic flowchart as Mermaid."""
    return Agent(
        name="ABB PLC Flowchart Generator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "Generate a clear, symbol-compliant Mermaid flowchart for ABB PLC logic (diamonds for decisions, rectangles for process steps).",
            "Include all safety, diagnostics, and process interlocks as per ABB best practices.",
            "Return only valid Mermaid code in a fenced block."
        ],
        markdown=True,
    )


def make_hmi_agent():
    """Create ABB HMI mockup as HTML/CSS."""
    return Agent(
        name="ABB HMI Generator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "Produce a clean, functional HMI HTML mockup that matches ABB CP600 or similar HMI styling (industrial colors, simple layouts, typical button/indicator arrangement).",
            "Only provide a clean HTML/CSS code block, using ABB HMI color palettes and iconography when possible."
        ],
        markdown=True,
    )


def make_simulation_agent():
    """Test scenario table for ABB PLC code."""
    return Agent(
        name="ABB PLC Logic Simulator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "Generate comprehensive test cases for ABB IEC 61131-3 Structured Text code, including normal running, edge conditions, and ABB-specific safety/fault cases.",
            "Present input conditions, expected outputs, and engineering logic in a markdown table."
        ],
        markdown=True,
    )


def make_validation_agent():
    """Validate ABB IEC 61131-3 code for compliance/safety."""
    return Agent(
        name="ABB IEC 61131-3 Validator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "Thoroughly validate Structured Text code for ABB PLCs: syntax, block structure, variable/data type consistency, safety (emergency stop logic, hazard interlocks), and compliance with IEC 61131-3 + ABB standards.",
            "Provide a pass/fail verdict and detailed analysis with targeted suggestions per ABB best practices.",
            "Do not provide any score or numerical rating."
        ],
        markdown=True,
    )


