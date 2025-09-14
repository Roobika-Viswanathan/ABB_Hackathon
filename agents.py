from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from plc_config import PLCConfig

def make_language_agent():
    """Create language normalization agent."""
    return Agent(
        name="Language Normalizer",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "Detect the input language. If not English, translate to clear technical English suitable for PLC code generation.",
            "Return only the English version of the user's requirement.",
            "Preserve all technical details and specifications."
        ],
        markdown=False,
    )

def make_clarification_agent():
    """Create requirements clarification agent."""
    return Agent(
        name="PLC Requirements Clarifier",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "You are an expert PLC programmer who helps clarify automation requirements.",
            "Analyze the user's input and determine if you need more information.",
            "If the input is clear and complete, respond with: CLEAR_INPUT",
            "Otherwise, ask ONE concise technical clarification question.",
            "Focus on missing technical specifications, safety requirements, or operational details."
        ],
        markdown=True,
    )

def make_enhanced_code_agent():
    """Create IEC 61131-3 code generation agent."""
    return Agent(
        name="IEC 61131-3 Code Generator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        tools=[DuckDuckGo(search=True)],
        instructions=[
            "You are an expert in PLC programming following IEC 61131-3 standard.",
            "Generate clean, well-commented Structured Text code with proper VAR blocks.",
            "Include proper variable declarations, data types, and safety considerations.",
            "Use appropriate timers, counters, and logic blocks as needed.",
            "Return ONLY valid IEC 61131-3 Structured Text code in a fenced code block.",
            "Include comments explaining the logic and safety features."
        ],
        markdown=True,
    )

def make_enhanced_flow_agent():
    """Create flowchart generation agent."""
    return Agent(
        name="IEC 61131-3 Flowchart Generator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "Generate a detailed Mermaid flowchart representing the PLC control logic.",
            "Use proper flowchart symbols (diamond for decisions, rectangle for processes).",
            "Include all conditions, actions, and safety interlocks.",
            "Make the flowchart clear and easy to follow.",
            "Return only valid Mermaid flowchart code in a fenced block."
        ],
        markdown=True,
    )

def make_hmi_agent():
    """Create HMI generation agent."""
    return Agent(
        name="HMI Generator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "Generate a professional HMI mockup as HTML with inline CSS.",
            "Include relevant controls, indicators, and displays for the PLC system.",
            "Use industrial-style colors and layouts.",
            "Make it functional-looking but as a mockup only.",
            "Return only clean HTML code in a fenced block."
        ],
        markdown=True,
    )

def make_simulation_agent():
    """Create simulation agent."""
    return Agent(
        name="PLC Logic Simulator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "Create comprehensive test scenarios for the provided IEC 61131-3 code.",
            "Include normal operation, edge cases, and failure modes.",
            "Present results in a clear markdown table format.",
            "Cover input conditions, expected outputs, and reasoning."
        ],
        markdown=True,
    )

def make_validation_agent():
    """Create code validation agent."""
    return Agent(
        name="IEC 61131-3 Validator",
        model=Groq(id=PLCConfig.DEFAULT_MODEL),
        instructions=[
            "You are an expert IEC 61131-3 syntax and safety validator.",
            "Thoroughly analyze the provided Structured Text code for:",
            "- Syntax correctness and proper block structures",
            "- Variable declarations and data type consistency", 
            "- Safety considerations and interlocks",
            "- Industrial best practices and standards compliance",
            "Provide a clear verdict and detailed analysis.",
            "Rate the code quality from 1-10 and suggest specific improvements."
        ],
        markdown=True,
    )
