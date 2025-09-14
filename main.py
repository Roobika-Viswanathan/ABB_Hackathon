# main.py (updated with working speech-to-text)

import streamlit as st
from streamlit.components.v1 import html as st_html
from plc_session import PLCSessionState
from handlers import (
    handle_generate_code, handle_generate_flowchart, handle_generate_both,
    handle_generate_hmi, handle_validate_and_simulate, export_complete_project
)
from utils import preprocess_input, validate_plc_requirements
import datetime

st.set_page_config(
    page_title="IEC 61131-3 Code Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

PLCSessionState.initialize()

def render_speech_to_text():
    """Render the Web Speech API component."""
    speech_to_text_html = """
    <button id="start-btn" style="background-color: #FF6B6B; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px;">🎤 Start Recording</button>
    <div id="output" style="margin-top:10px; font-size:1.2em; color:#333; border:1px solid #ddd; padding:10px; border-radius:5px; min-height:40px; background-color:#f9f9f9;"></div>
    <textarea id="recognized-text" style="width: 100%; height: 80px; margin-top: 10px; padding: 8px; border: 1px solid #ddd; border-radius: 5px;" placeholder="Recognized text will appear here..."></textarea>

    <script>
    const btn = document.getElementById('start-btn');
    const output = document.getElementById('output');
    const textarea = document.getElementById('recognized-text');

    let recognizing = false;
    let recognition;

    if (!('webkitSpeechRecognition' in window)) {
      output.textContent = 'Web Speech API not supported in this browser. Please use Chrome or Edge.';
      btn.disabled = true;
    } else {
      recognition = new webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        recognizing = true;
        btn.textContent = '🔴 Listening... Click to Stop';
        btn.style.backgroundColor = '#FF4444';
        output.textContent = 'Listening...';
      };

      recognition.onerror = (event) => {
        output.textContent = 'Error: ' + event.error;
        btn.textContent = '🎤 Start Recording';
        btn.style.backgroundColor = '#FF6B6B';
        recognizing = false;
      };

      recognition.onend = () => {
        recognizing = false;
        btn.textContent = '🎤 Start Recording';
        btn.style.backgroundColor = '#FF6B6B';
      };

      recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        
        const fullTranscript = finalTranscript + interimTranscript;
        textarea.value = fullTranscript;
        output.textContent = fullTranscript || 'Listening...';
      };
    }

    btn.onclick = () => {
      if (recognizing) {
        recognition.stop();
      } else {
        recognition.start();
      }
    };
    </script>
    """
    
    st_html(speech_to_text_html, height=200)

def render_sidebar():
    """Render the sidebar with settings and information."""
    st.sidebar.header("🔧 Settings")
    
    st.sidebar.subheader("Agent Configuration")
    st.session_state.use_rag = st.sidebar.checkbox("Use Knowledge Base (RAG)", value=st.session_state.use_rag)
    st.session_state.multilingual = st.sidebar.checkbox("Multilingual Input", value=st.session_state.multilingual)
    
    if st.session_state.use_rag:
        if st.session_state.kb_index:
            st.sidebar.success(f"KB loaded: {len(st.session_state.kb_index)} chunks")
        else:
            st.sidebar.info("No knowledge base found. Create a 'kb' folder with reference documents.")
    
    st.sidebar.subheader("Current Input Analysis")
    if hasattr(st.session_state, 'last_prompt') and st.session_state.last_prompt:
        analysis = preprocess_input(st.session_state.last_prompt)
        for key, value in analysis.items():
            if isinstance(value, bool):
                st.sidebar.text(f"{key.replace('_', ' ').title()}: {'✅' if value else '❌'}")
            else:
                st.sidebar.text(f"{key.replace('_', ' ').title()}: {value}")
    
    st.sidebar.subheader("Conversation History")
    if st.session_state.conversation_history:
        for i, msg in enumerate(st.session_state.conversation_history[-3:]):
            st.sidebar.text(f"{i+1}. {msg[:50]}...")
    else:
        st.sidebar.text("No conversation yet")

def main():
    """Main Streamlit application."""
    
    st.title("🤖 AI-Powered IEC 61131-3 Code Generator")
    st.markdown("*Transform natural language into professional PLC code with voice input and AI agents*")
    
    # Input Mode Selection
    st.header("🎙️ Input Mode")
    input_mode = st.radio("Choose input mode:", ["Text", "Voice"])
    
    nl_input = ""
    
    if input_mode == "Text":
        nl_input = st.text_area(
            "Enter your control logic (natural language):",
            placeholder="e.g., Turn ON motor when temperature exceeds 50°C and pressure is below 100 bar, turn OFF when temperature drops below 45°C",
            value=st.session_state.last_prompt,
            height=100,
            help="Describe your automation logic in plain language. Include conditions, actions, and safety requirements."
        )
    
    elif input_mode == "Voice":
        st.info("🎤 Click 'Start Recording' below, speak clearly, then use the recognized text.")
        
        # Render the speech-to-text component
        render_speech_to_text()
        
        # Get recognized text from user
        recognized_input = st.text_area(
            "Recognized/Edit text:",
            placeholder="Recognized text will appear here after recording...",
            help="The recognized speech will appear here. You can edit it before using."
        )
        
        if st.button("Use Recognized Text", type="primary"):
            if recognized_input.strip():
                nl_input = recognized_input
                st.session_state.last_prompt = recognized_input
                st.success(f"✅ Using recognized text: {recognized_input}")
                st.rerun()
            else:
                st.warning("No recognized text to use. Please record some speech first.")
    
    # Input Analysis Display
    if nl_input:
        analysis = preprocess_input(nl_input)
        validation = validate_plc_requirements(nl_input)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", analysis["word_count"])
        with col2:
            st.metric("Complexity", analysis["complexity"].title())
        with col3:
            st.metric("Confidence", f"{validation['confidence']:.1%}")
    
    # Clarification handling
    if st.session_state.clarification_needed:
        st.warning("⚠ Clarification Needed")
        st.info(st.session_state.clarification_question)
        
        clarification_response = st.text_input(
            "Your response:",
            placeholder="Please provide the requested information...",
            help="Answer the clarification question to proceed with code generation."
        )
        
        col_clear, col_proceed = st.columns(2)
        with col_clear:
            if st.button("Clear Clarification", type="secondary"):
                st.session_state.clarification_needed = False
                st.session_state.clarification_question = ""
                st.rerun()
        
        with col_proceed:
            if st.button("Proceed with Clarification", type="primary") and clarification_response.strip():
                st.session_state.context_info['clarification'] = clarification_response
                st.session_state.conversation_history.append(f"Q: {st.session_state.clarification_question}")
                st.session_state.conversation_history.append(f"A: {clarification_response}")
                st.session_state.clarification_needed = False
                st.session_state.clarification_question = ""
                st.success("Clarification received! You can now generate code.")
                st.rerun()
    
    # Generation buttons
    st.header("🔧 Generate PLC Components")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        gen_code_clicked = st.button("Generate Code", type="primary", use_container_width=True)
    with col2:
        gen_flow_clicked = st.button("Generate Flowchart", use_container_width=True)
    with col3:
        gen_both_clicked = st.button("Generate Both", use_container_width=True)
    
    col4, col5 = st.columns(2)
    with col4:
        gen_hmi_clicked = st.button("Generate HMI", use_container_width=True)
    with col5:
        validate_sim_clicked = st.button("Validate & Simulate", use_container_width=True)
    
    # Handle button clicks
    if gen_code_clicked:
        handle_generate_code(nl_input)
    if gen_flow_clicked:
        handle_generate_flowchart(nl_input)
    if gen_both_clicked:
        handle_generate_both(nl_input)
    if gen_hmi_clicked:
        handle_generate_hmi(nl_input)
    if validate_sim_clicked:
        handle_validate_and_simulate()
    
    # Display results in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 IEC 61131-3 Code", "📊 Flowchart", "🖥️ HMI", "✅ Validation/Simulation"])
    
    with tab1:
        st.markdown("### Generated IEC 61131-3 Code")
        if st.session_state.generated_code:
            st.code(st.session_state.generated_code, language="pascal")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    label="Download Code",
                    data=st.session_state.generated_code,
                    file_name="plc_code.st",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                if st.button("Refine Code", use_container_width=True):
                    st.session_state.show_refinement = True
            with col3:
                if st.button("Quick Validate", use_container_width=True):
                    from agents import make_validation_agent
                    from utils import safe_agent_run
                    validation_agent = make_validation_agent()
                    result = safe_agent_run(validation_agent, st.session_state.generated_code, "Quick validation")
                    st.info(result)
        else:
            st.info("No code generated yet. Click 'Generate Code' to start.")
    
    with tab2:
        st.markdown("### Generated Flowchart")
        if st.session_state.generated_flowchart:
            st.markdown(st.session_state.generated_flowchart)
        else:
            st.info("No flowchart generated yet. Click 'Generate Flowchart' to start.")
    
    with tab3:
        st.markdown("### HMI Mockup")
        if st.session_state.generated_hmi:
            st_html(st.session_state.generated_hmi, height=520)
            st.download_button(
                label="Download HMI",
                data=st.session_state.generated_hmi,
                file_name="hmi_mockup.html",
                mime="text/html"
            )
        else:
            st.info("No HMI generated yet. Click 'Generate HMI' to start.")
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Validation Report")
            if st.session_state.validation_report:
                st.markdown(st.session_state.validation_report)
            else:
                st.info("No validation report yet.")
        
        with col2:
            st.markdown("#### Simulation Results")
            if st.session_state.simulation_report:
                st.markdown(st.session_state.simulation_report)
            else:
                st.info("No simulation results yet.")
    
    # Code refinement section
    if hasattr(st.session_state, 'show_refinement') and st.session_state.show_refinement:
        st.header("🔧 Code Refinement")
        refinement_request = st.text_input(
            "What would you like to improve?",
            placeholder="e.g., Add safety interlocks, optimize performance, add error handling",
            help="Describe specific improvements you want to make to the generated code."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Apply Refinement", type="primary") and refinement_request.strip():
                from agents import Agent
                from phi.model.groq import Groq
                from utils import safe_agent_run, extract_first_code_block
                from handlers import save_code_version
                
                refinement_agent = Agent(
                    name="PLC Code Optimizer",
                    model=Groq(id="llama-3.3-70b-versatile"),
                    instructions=[
                        "You are a senior PLC programmer specializing in code optimization.",
                        "Improve the provided IEC 61131-3 code based on the user's request.",
                        "Maintain original functionality while adding requested improvements.",
                        "Follow industrial best practices for safety and reliability.",
                        "Return improved code in a fenced code block with explanatory comments."
                    ],
                    markdown=True,
                )
                
                refinement_prompt = f"Original code:\n{st.session_state.generated_code}\n\nRefinement request: {refinement_request}"
                refined_response = safe_agent_run(refinement_agent, refinement_prompt, "Code refinement")
                
                refined_code = extract_first_code_block(refined_response)
                if refined_code:
                    save_code_version("Before refinement")
                    st.session_state.generated_code = refined_code
                    st.success("Code refined successfully!")
                    st.rerun()
        
        with col2:
            if st.button("Cancel Refinement", type="secondary"):
                st.session_state.show_refinement = False
                st.rerun()
    
    # Export and history section
    st.header("📦 Export & History")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Project", use_container_width=True):
            if any([st.session_state.generated_code, st.session_state.generated_flowchart, st.session_state.generated_hmi]):
                zip_data = export_complete_project()
                st.download_button(
                    label="Download ZIP",
                    data=zip_data,
                    file_name=f"plc_project_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            else:
                st.warning("No generated content to export.")
    
    with col2:
        if st.button("Version History", use_container_width=True):
            if st.session_state.code_versions:
                st.subheader("Code Version History")
                for i, version in enumerate(reversed(st.session_state.code_versions[-5:])):
                    with st.expander(f"Version {len(st.session_state.code_versions)-i}: {version['description']}"):
                        st.text(f"Timestamp: {version['timestamp']}")
                        st.text(f"Prompt: {version['prompt']}")
                        st.code(version['code'], language="pascal")
            else:
                st.info("No version history available.")
    
    with col3:
        if st.button("🗑 Clear All", type="secondary", use_container_width=True):
            if st.button("Confirm Clear", type="secondary"):
                PLCSessionState.clear_session()
                st.success("Session cleared!")
                st.rerun()

if __name__ == "__main__":
    render_sidebar()
    main()
