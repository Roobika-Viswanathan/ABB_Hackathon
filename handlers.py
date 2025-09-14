import datetime
import io
import zipfile
import streamlit as st
import textwrap
from utils import (
    preprocess_input, validate_plc_requirements, safe_agent_run,
    extract_first_code_block, compose_rag_context
)
from agents import (
    make_language_agent, make_clarification_agent, make_enhanced_code_agent,
    make_enhanced_flow_agent, make_hmi_agent, make_validation_agent,
    make_simulation_agent
)
from plc_session import PLCSessionState


def save_code_version(description="Auto-save"):
    """Save current code as a version."""
    if st.session_state.generated_code:
        version = {
            "timestamp": datetime.datetime.now().isoformat(),
            "code": st.session_state.generated_code,
            "description": description,
            "prompt": st.session_state.last_prompt
        }
        st.session_state.code_versions.append(version)


def export_complete_project():
    """Export all generated artifacts as a zip file."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        if st.session_state.generated_code:
            zip_file.writestr("plc_code.st", st.session_state.generated_code)
        if st.session_state.generated_flowchart:
            zip_file.writestr("flowchart.md", st.session_state.generated_flowchart)
        if st.session_state.generated_hmi:
            zip_file.writestr("hmi_mockup.html", st.session_state.generated_hmi)
        if st.session_state.validation_report:
            zip_file.writestr("validation_report.md", st.session_state.validation_report)
        if st.session_state.simulation_report:
            zip_file.writestr("simulation_report.md", st.session_state.simulation_report)
    
    return zip_buffer.getvalue()


def handle_generate_code(prompt: str):
    """Handle code generation with improved error handling."""
    if not prompt.strip():
        st.warning("Please enter some control logic.")
        return
    
    validation = validate_plc_requirements(prompt)
    if not validation["is_valid"]:
        for warning in validation["warnings"]:
            st.warning(warning)
        return
    
    for suggestion in validation["suggestions"]:
        st.info(f"💡 Suggestion: {suggestion}")
    
    normalized = prompt
    if st.session_state.multilingual:
        with st.spinner("Normalizing language..."):
            lang_agent = make_language_agent()
            normalized = safe_agent_run(lang_agent, prompt, "Language normalization")
    
    if not st.session_state.clarification_needed:
        analysis = preprocess_input(normalized)
        
        with st.spinner("Analyzing requirements..."):
            clarification_agent = make_clarification_agent()
            context_prompt = f"User input: {normalized}\n\nInput analysis: {analysis}"
            clarification_response = safe_agent_run(clarification_agent, context_prompt, "Requirements analysis")
        
        if "CLEAR_INPUT" not in clarification_response.upper():
            st.session_state.clarification_needed = True
            st.session_state.clarification_question = clarification_response
            st.rerun()
            return
    
    st.session_state.last_prompt = normalized
    
    with st.spinner("Generating IEC 61131-3 code..."):
        agent = make_enhanced_code_agent()
        enhanced_prompt = normalized
        
        rag_block = compose_rag_context(normalized) if st.session_state.use_rag else ""
        if rag_block:
            enhanced_prompt += "\n\nReference Context (from KB):\n" + rag_block
        
        response = safe_agent_run(agent, enhanced_prompt, "Code generation")
        code_only = extract_first_code_block(response) or response
        st.session_state.generated_code = code_only
        
        save_code_version("Generated from prompt")
        
        st.session_state.conversation_history.append(f"Generated code for: {normalized}")
    
    st.success("Code generated successfully!")


def handle_generate_flowchart(prompt: str):
    """Handle flowchart generation."""
    if not prompt.strip():
        st.warning("Please enter some control logic.")
        return
    
    st.session_state.last_prompt = prompt
    
    with st.spinner("Generating flowchart..."):
        agent = make_enhanced_flow_agent()
        enhanced_prompt = prompt
        
        rag_block = compose_rag_context(prompt) if st.session_state.use_rag else ""
        if rag_block:
            enhanced_prompt += "\n\nReference Context (from KB):\n" + rag_block
        
        response = safe_agent_run(agent, enhanced_prompt, "Flowchart generation")
        st.session_state.generated_flowchart = response
        
        st.session_state.conversation_history.append(f"Generated flowchart for: {prompt}")
    
    st.success("Flowchart generated successfully!")


def handle_generate_both(prompt: str):
    """Handle generation of both code and flowchart."""
    handle_generate_code(prompt)
    if not st.session_state.clarification_needed:
        handle_generate_flowchart(prompt)


def handle_generate_hmi(prompt: str):
    if not prompt.strip():
        st.warning("Please enter some control logic.")
        return
    
    with st.spinner("Generating HMI mockup..."):
        agent = make_hmi_agent()
        enhanced_prompt = prompt
        
        rag_block = compose_rag_context(prompt) if st.session_state.use_rag else ""
        if rag_block:
            enhanced_prompt += "\n\nReference Context (from KB):\n" + rag_block
        
        response = safe_agent_run(agent, enhanced_prompt, "HMI generation")
        html_block = extract_first_code_block(response)
        st.session_state.generated_hmi = html_block or "<div>HMI generation failed.</div>"
        st.success("HMI generated!")


def handle_validate_and_simulate():
    """Handle validation and simulation."""
    if not st.session_state.generated_code:
        st.warning("Please generate code first!")
        return
    
    with st.spinner("Running validation & simulation..."):
        validation_agent = make_validation_agent()
        validation_response = safe_agent_run(validation_agent, st.session_state.generated_code, "Code validation")
        st.session_state.validation_report = validation_response
        
        sim_agent = make_simulation_agent()
        sim_prompt = textwrap.dedent(f"""
            Requirements (for context): {st.session_state.last_prompt}
            Code under test:
            ```
            {st.session_state.generated_code}
            ```
            Create a comprehensive table of test scenarios including normal operation, edge cases, and failure modes.
        """)
        simulation_response = safe_agent_run(sim_agent, sim_prompt, "Logic simulation")
        st.session_state.simulation_report = simulation_response
