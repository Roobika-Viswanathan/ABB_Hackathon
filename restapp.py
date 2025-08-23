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

def extract_first_code_block(text: str) -> str | None:
    """
    Extracts the FIRST fenced code block from text and returns only its inner content.
    Supports ```lang\n...\n``` and ```\n...\n```.
    """
    if not text:
        return None
    m = re.search(r"```(?:[a-zA-Z0-9_-]+)?\s*\n(.*?)\n```", text, flags=re.DOTALL)
    if m:
        return m.group(1).strip()
    return None

init_state()

st.set_page_config(page_title="IEC 61131-3 Code Generator", layout="wide")
st.title("AI-Powered IEC 61131-3 Code Generator")

st.header("Transform Natural Language into IEC 61131-3 Standard Code + Flowchart")

nl_input = st.text_area(
    "Enter your control logic (natural language):",
    placeholder="e.g., Turn ON motor if temperature > 50 and pressure < 100",
    value=st.session_state.last_prompt,
)

colA, colB, colC = st.columns(3)

with colA:
    gen_code_clicked = st.button("Generate Code")
with colB:
    gen_flow_clicked = st.button("Generate Flowchart")
with colC:
    gen_both_clicked = st.button("Generate Both")

def make_code_agent():
    return Agent(
        name="IEC 61131-3 Code Generator",
        model=Groq(id="llama-3.3-70b-versatile"),
        tools=[DuckDuckGo(search=True)],
        instructions=[
            "You are an expert in industrial automation and PLC programming.",
            "Use DuckDuckGo to confirm IEC 61131-3 Structured Text syntax if needed.",
            "Convert natural language control logic into IEC 61131-3 Structured Text code.",
            "Ensure correct syntax (VAR blocks as needed, IF/THEN/END_IF, correct operators, := assignments).",
            "Return only the IEC 61131-3 Structured Text inside a fenced code block.",
            "make sure to give correct code on first attempt"
        ],
        markdown=True,
        debug_mode=True,
    )

def make_flow_agent():
    return Agent(
        name="IEC 61131-3 Flowchart Generator",
        model=Groq(id="llama-3.3-70b-versatile"),
        tools=[DuckDuckGo(search=True)],
        instructions=[
            "You are an expert in industrial automation and PLC programming.",
            "Understand the natural language input and generate a flowchart.",
            "The flowchart must be written using Mermaid syntax inside a fenced block: ```mermaid ... ```",
            "Ensure decision points and actions are clearly represented.",
        ],
        markdown=True,
        debug_mode=True,
    )

def handle_generate_code(prompt: str):
    if not prompt.strip():
        st.warning("Please enter some control logic.")
        return
    st.session_state.last_prompt = prompt
    with st.spinner("Generating IEC 61131-3 code..."):
        agent = make_code_agent()
        resp = agent.run(prompt)
        content = getattr(resp, "content", str(resp))
        code_only = extract_first_code_block(content) or content
        st.session_state.generated_code = code_only
    st.success("Code generated and saved for validation.")

def handle_generate_flowchart(prompt: str):
    if not prompt.strip():
        st.warning("Please enter some control logic.")
        return
    st.session_state.last_prompt = prompt
    with st.spinner("Generating flowchart..."):
        agent = make_flow_agent()
        resp = agent.run(prompt)
        content = getattr(resp, "content", str(resp))
        st.session_state.generated_flowchart = content
    st.success("Flowchart generated.")

def handle_generate_both(prompt: str):
    handle_generate_code(prompt)
    handle_generate_flowchart(prompt)

if gen_code_clicked:
    handle_generate_code(nl_input)
if gen_flow_clicked:
    handle_generate_flowchart(nl_input)
if gen_both_clicked:
    handle_generate_both(nl_input)

tab1, tab2 = st.tabs(["IEC 61131-3 Code", "Flowchart"])
with tab1:
    st.markdown("## Generated IEC 61131-3 Code")
    if st.session_state.generated_code:
        st.code(st.session_state.generated_code, language="iecst")
    else:
        st.info("No code generated yet.")

with tab2:
    st.markdown("## Generated Flowchart")
    if st.session_state.generated_flowchart:
        st.markdown(st.session_state.generated_flowchart)
    else:
        st.info("No flowchart generated yet.")

st.header("Validation")
if st.button("Validate Code Syntax"):
    if not st.session_state.generated_code:
        st.warning("Please generate code first!")
    else:
        with st.spinner("Validating IEC 61131-3 code..."):
            validation_agent = Agent(
                name="IEC 61131-3 Validator",
                model=Groq(id="llama-3.3-70b-versatile"),
                instructions=[
                    "You are an IEC 61131-3 syntax and PLC code validation expert.",
                    "Analyze ONLY the provided IEC 61131-3 Structured Text code.",
                    "Check syntax correctness: VAR blocks, assignments (:=), operators (AND, OR, NOT), IF/THEN/END_IF, CASE/END_CASE, loops, END statements.",
                    "Identify common mistakes (missing END_IF/END_CASE/END_FOR, invalid keywords, wrong comparison or logical operators, missing semicolons).",
                    "If errors exist, list them clearly and provide a corrected code version in a fenced code block.",
                    "If the code is valid, respond exactly with: Valid Code - No issues found.",
                ],
                markdown=True,
                debug_mode=True,
            )
            validation_response = validation_agent.run(st.session_state.generated_code)
            st.markdown("## Validation Result")
            st.markdown(getattr(validation_response, "content", str(validation_response)))

st.sidebar.header("Debug Info")
st.sidebar.write("Debug mode is enabled for detailed responses.")
st.sidebar.subheader("Last Prompt")
st.sidebar.write(st.session_state.last_prompt or "—")
st.sidebar.subheader("Persisted Code (for validation)")
st.sidebar.code(st.session_state.generated_code or "—", language="iecst")
