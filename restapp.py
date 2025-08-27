import os
import re
import streamlit as st
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo

load_dotenv()

def init_state():
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = None
    if "generated_flowchart" not in st.session_state:
        st.session_state.generated_flowchart = None
    if "last_prompt" not in st.session_state:
        st.session_state.last_prompt = ""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "clarification_needed" not in st.session_state:
        st.session_state.clarification_needed = False
    if "clarification_question" not in st.session_state:
        st.session_state.clarification_question = ""
    if "context_info" not in st.session_state:
        st.session_state.context_info = {}

def extract_first_code_block(text: str) -> str | None:
    """
    Extracts the FIRST fenced code block from text and returns only its inner content.
    Supports `````` and ``````.
    """
    if not text:
        return None
    m = re.search(r"``````", text, flags=re.DOTALL)
    if m:
        return m.group(1).strip()
    return None

def preprocess_input(user_input: str) -> dict:
    """
    Analyze user input to identify key components and potential ambiguities.
    """
    analysis = {
        "has_conditions": bool(re.search(r'\b(if|when|while|until)\b', user_input.lower())),
        "has_sensors": bool(re.search(r'\b(temperature|pressure|level|flow|sensor)\b', user_input.lower())),
        "has_actuators": bool(re.search(r'\b(motor|pump|valve|heater|fan|light)\b', user_input.lower())),
        "has_values": bool(re.search(r'\d+', user_input)),
        "has_operators": bool(re.search(r'\b(and|or|not|greater|less|equal)\b', user_input.lower())),
        "complexity": len(user_input.split()) > 10,
        "ambiguous_terms": []
    }
    
    ambiguous_patterns = [
        (r'\bhigh\b', 'high (what value?)'),
        (r'\blow\b', 'low (what value?)'),
        (r'\bon\b', 'on (for how long?)'),
        (r'\boff\b', 'off (under what conditions?)'),
        (r'\bstart\b', 'start (what sequence?)'),
        (r'\bstop\b', 'stop (emergency or normal?)'),
    ]
    
    for pattern, suggestion in ambiguous_patterns:
        if re.search(pattern, user_input.lower()):
            analysis['ambiguous_terms'].append(suggestion)
    
    return analysis

def make_clarification_agent():
    return Agent(
        name="PLC Requirements Clarifier",
        model=Groq(id="llama-3.3-70b-versatile"),
        instructions=[
            "You are an expert PLC programmer who helps clarify automation requirements.",
            "Analyze the user's input and determine if you need more information to generate accurate IEC 61131-3 code.",
            "If the input is clear and complete, respond with: CLEAR_INPUT",
            "If clarification is needed, ask ONE specific question about the most critical missing information.",
            "Focus on: specific values, timing requirements, safety conditions, or ambiguous terms.",
            "Keep questions concise and technical.",
            "Examples of good questions:",
            "- What temperature threshold should trigger the motor? (you mentioned 'high temperature')",
            "- Should the motor stop automatically or require manual intervention?",
            "- What is the normal operating pressure range?",
        ],
        markdown=True,
        debug_mode=False,
    )

def make_enhanced_code_agent():
    return Agent(
        name="IEC 61131-3 Code Generator",
        model=Groq(id="llama-3.3-70b-versatile"),
        tools=[DuckDuckGo(search=True)],
        instructions=[
            "You are an expert in industrial automation and PLC programming with 15+ years experience.",
            "Generate IEC 61131-3 Structured Text code based on the requirements.",
            "ALWAYS include proper variable declarations in VAR...END_VAR blocks.",
            "Use descriptive variable names (e.g., Temperature_Sensor, Motor_Start, Pressure_High).",
            "Include comments for complex logic.",
            "Follow IEC 61131-3 syntax strictly:",
            "  - Use := for assignments",
            "  - Use AND, OR, NOT for boolean operations", 
            "  - Use proper comparison operators (>, <, >=, <=, =, <>)",
            "  - Always close blocks (END_IF, END_CASE, END_FOR, END_WHILE)",
            "  - End statements with semicolons",
            "Return ONLY the IEC 61131-3 code in a fenced code block.",
            "Test your code mentally before providing it - ensure all blocks are closed and syntax is correct."
        ],
        markdown=True,
        debug_mode=False,
    )

def make_enhanced_flow_agent():
    return Agent(
        name="IEC 61131-3 Flowchart Generator",
        model=Groq(id="llama-3.3-70b-versatile"),
        tools=[DuckDuckGo(search=True)],
        instructions=[
            "You are an expert in industrial automation flowchart design.",
            "Create a detailed Mermaid flowchart that represents the control logic.",
            "Use proper flowchart symbols:",
            "  - Rectangles for processes/actions",
            "  - Diamonds for decisions/conditions", 
            "  - Circles for start/end",
            "Include all sensors, conditions, and actuators from the logic.",
            "Use descriptive labels and show the flow clearly.",
            "Return the flowchart in mermaid code block format with triple backticks.",
            "Use standard flowchart structure with proper syntax."
        ],
        markdown=True,
        debug_mode=False,
    )

init_state()

st.set_page_config(page_title="IEC 61131-3 Code Generator", layout="wide")
st.title("🤖 AI-Powered IEC 61131-3 Code Generator")

st.header("Transform Natural Language into IEC 61131-3 Standard Code + Flowchart")

nl_input = st.text_area(
    "Enter your control logic (natural language):",
    placeholder="e.g., Turn ON motor when temperature exceeds 50C and pressure is below 100 bar, turn OFF when temperature drops below 45C",
    value=st.session_state.last_prompt,
    height=100
)

if st.session_state.clarification_needed:
    st.warning("⚠️ Clarification Needed")
    st.info(st.session_state.clarification_question)
    
    clarification_response = st.text_input(
        "Your response:",
        placeholder="Please provide the requested information..."
    )
    
    col_clear, col_proceed = st.columns(2)
    with col_clear:
        if st.button("Clear Clarification"):
            st.session_state.clarification_needed = False
            st.session_state.clarification_question = ""
            st.rerun()
    
    with col_proceed:
        if st.button("Proceed with Clarification") and clarification_response.strip():
            st.session_state.context_info['clarification'] = clarification_response
            st.session_state.conversation_history.append(f"Q: {st.session_state.clarification_question}")
            st.session_state.conversation_history.append(f"A: {clarification_response}")
            st.session_state.clarification_needed = False
            st.session_state.clarification_question = ""
            st.success("Clarification received! You can now generate code.")
            st.rerun()

colA, colB, colC = st.columns(3)

with colA:
    gen_code_clicked = st.button("🔧 Generate Code")
with colB:
    gen_flow_clicked = st.button("📊 Generate Flowchart")
with colC:
    gen_both_clicked = st.button("🚀 Generate Both")

def build_context_prompt(original_prompt: str) -> str:
    """Build enhanced prompt with conversation history and context."""
    context_prompt = original_prompt
    
    if st.session_state.conversation_history:
        context_prompt += "\n\nPrevious conversation:\n" + "\n".join(st.session_state.conversation_history[-4:])
    
    if st.session_state.context_info:
        context_prompt += "\n\nAdditional context:\n"
        for key, value in st.session_state.context_info.items():
            context_prompt += f"- {key}: {value}\n"
    
    return context_prompt

def handle_generate_code(prompt: str):
    if not prompt.strip():
        st.warning("Please enter some control logic.")
        return
    
    if not st.session_state.clarification_needed:
        analysis = preprocess_input(prompt)
        
        with st.spinner("Analyzing requirements..."):
            clarification_agent = make_clarification_agent()
            context_prompt = f"User input: {prompt}\n\nInput analysis: {analysis}"
            clarification_response = clarification_agent.run(context_prompt)
            clarification_content = getattr(clarification_response, "content", str(clarification_response))
        
        if "CLEAR_INPUT" not in clarification_content.upper():
            st.session_state.clarification_needed = True
            st.session_state.clarification_question = clarification_content
            st.rerun()
            return
    
    st.session_state.last_prompt = prompt
    
    with st.spinner("Generating IEC 61131-3 code..."):
        agent = make_enhanced_code_agent()
        enhanced_prompt = build_context_prompt(prompt)
        resp = agent.run(enhanced_prompt)
        content = getattr(resp, "content", str(resp))
        code_only = extract_first_code_block(content) or content
        st.session_state.generated_code = code_only
        
        st.session_state.conversation_history.append(f"Generated code for: {prompt}")
    
    st.success("✅ Code generated successfully!")

def handle_generate_flowchart(prompt: str):
    if not prompt.strip():
        st.warning("Please enter some control logic.")
        return
    
    st.session_state.last_prompt = prompt
    
    with st.spinner("Generating flowchart..."):
        agent = make_enhanced_flow_agent()
        enhanced_prompt = build_context_prompt(prompt)
        resp = agent.run(enhanced_prompt)
        content = getattr(resp, "content", str(resp))
        st.session_state.generated_flowchart = content
        
        st.session_state.conversation_history.append(f"Generated flowchart for: {prompt}")
    
    st.success("✅ Flowchart generated successfully!")

def handle_generate_both(prompt: str):
    handle_generate_code(prompt)
    if not st.session_state.clarification_needed:  
        handle_generate_flowchart(prompt)

if gen_code_clicked:
    handle_generate_code(nl_input)
if gen_flow_clicked:
    handle_generate_flowchart(nl_input)
if gen_both_clicked:
    handle_generate_both(nl_input)

tab1, tab2 = st.tabs(["📝 IEC 61131-3 Code", "📊 Flowchart"])

with tab1:
    st.markdown("## Generated IEC 61131-3 Code")
    if st.session_state.generated_code:
        st.code(st.session_state.generated_code, language="iecst")
        
        st.download_button(
            label="💾 Download Code",
            data=st.session_state.generated_code,
            file_name="plc_code.st",
            mime="text/plain"
        )
    else:
        st.info("No code generated yet. Click 'Generate Code' to start.")

with tab2:
    st.markdown("## Generated Flowchart")
    if st.session_state.generated_flowchart:
        st.markdown(st.session_state.generated_flowchart)
    else:
        st.info("No flowchart generated yet. Click 'Generate Flowchart' to start.")

st.header("🔍 Code Validation & Refinement")
col_validate, col_refine = st.columns(2)

with col_validate:
    if st.button("✅ Validate Code Syntax"):
        if not st.session_state.generated_code:
            st.warning("Please generate code first!")
        else:
            with st.spinner("Validating IEC 61131-3 code..."):
                validation_agent = Agent(
                    name="IEC 61131-3 Validator",
                    model=Groq(id="llama-3.3-70b-versatile"),
                    instructions=[
                        "You are an IEC 61131-3 syntax and PLC code validation expert.",
                        "Analyze the provided IEC 61131-3 Structured Text code thoroughly.",
                        "Check for proper VAR block declarations, correct assignment operators, proper boolean operators, correct comparison operators, properly closed blocks, missing semicolons, variable naming conventions, and data type consistency.",
                        "If the code is valid, respond with: VALID CODE - No syntax issues found.",
                        "If errors exist, list them clearly and provide corrected code in a fenced block.",
                        "Rate the code quality on a scale of 1-10 and suggest improvements."
                    ],
                    markdown=True,
                    debug_mode=False,
                )
                validation_response = validation_agent.run(st.session_state.generated_code)
                st.markdown("### Validation Result")
                st.markdown(getattr(validation_response, "content", str(validation_response)))

with col_refine:
    if st.button("🔧 Refine Code"):
        if not st.session_state.generated_code:
            st.warning("Please generate code first!")
        else:
            refinement_request = st.text_input(
                "What would you like to improve?",
                placeholder="e.g., Add safety interlocks, optimize performance, add error handling"
            )
            
            if refinement_request:
                with st.spinner("Refining code..."):
                    refinement_agent = Agent(
                        name="PLC Code Optimizer",
                        model=Groq(id="llama-3.3-70b-versatile"),
                        instructions=[
                            "You are a senior PLC programmer specializing in code optimization.",
                            "Improve the provided IEC 61131-3 code based on the user's request.",
                            "Maintain the original functionality while adding requested improvements.",
                            "Follow industrial best practices for safety and reliability.",
                            "Return the improved code in a fenced code block with explanatory comments."
                        ],
                        markdown=True,
                        debug_mode=False,
                    )
                    
                    refinement_prompt = f"Original code:\n{st.session_state.generated_code}\n\nRefinement request: {refinement_request}"
                    refinement_response = refinement_agent.run(refinement_prompt)
                    
                    refined_code = extract_first_code_block(getattr(refinement_response, "content", str(refinement_response)))
                    if refined_code:
                        st.session_state.generated_code = refined_code
                        st.success("Code refined successfully!")
                        st.rerun()

st.sidebar.header("🔧 Session Info")
st.sidebar.subheader("Input Analysis")
if nl_input:
    analysis = preprocess_input(nl_input)
    st.sidebar.json(analysis)

st.sidebar.subheader("Conversation History")
if st.session_state.conversation_history:
    for i, msg in enumerate(st.session_state.conversation_history[-3:]):
        st.sidebar.text(f"{i+1}. {msg[:50]}...")
else:
    st.sidebar.write("No conversation yet")

st.sidebar.subheader("Current Context")
if st.session_state.context_info:
    for key, value in st.session_state.context_info.items():
        st.sidebar.write(f"**{key}**: {value}")

if st.sidebar.button("🗑️ Clear Session"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()
