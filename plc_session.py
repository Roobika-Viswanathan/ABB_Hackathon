import streamlit as st

class PLCSessionState:
    """Centralized session state management."""
    
    @staticmethod
    def initialize():
        """Initialize all session state variables."""
        defaults = {
            "generated_code": None,
            "generated_flowchart": None,
            "generated_hmi": None,
            "validation_report": None,
            "simulation_report": None,
            "last_prompt": "",
            "conversation_history": [],
            "clarification_needed": False,
            "clarification_question": "",
            "context_info": {},
            "kb_index": None,
            "use_rag": True,
            "multilingual": True,
            "code_versions": [],
            "recognized_text": ""
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value


    @staticmethod
    def clear_session():
        """Clear all session state."""
        for key in list(st.session_state.keys()):
            del st.session_state[key]

PLCSessionState.initialize()
