# 🤖 AI-Powered IEC 61131-3 Code Generator

A **Streamlit-based app** that converts **natural language control logic** into **IEC 61131-3 Structured Text (ST) code** and **flowcharts**.  
Designed for PLC programmers and automation engineers to accelerate development with AI assistance.  

---

## ✨ Features

- 🔧 **Generate PLC Code** – Natural language → IEC 61131-3 Structured Text  
- 📊 **Generate Flowcharts** – Mermaid diagrams of control logic  
- ⚡ **Clarification Agent** – Automatically asks questions when inputs are ambiguous  
- ✅ **Code Validator** – Checks syntax, conventions, and best practices  
- 🔧 **Code Refiner** – Add safety interlocks, optimize performance, or improve readability  
- 💾 **Download Support** – Save generated PLC code as `.st` files  
- 🖥️ **Session Context** – Maintains conversation history and clarifications  

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) – Web UI  
- [Phi Agents](https://github.com/phi-agent/phi) – AI agent orchestration  
- [Groq](https://groq.com/) – LLM inference engine  
- [DuckDuckGo API](https://duckduckgo.com/) – Knowledge lookup  

---

## 📂 Project Structure
├── app.py # Main Streamlit app
├── requirements.txt # Python dependencies
├── README.md # Documentation
└── .env # API keys and environment variables

---

## ⚙️ Installation

1. Clone the repository:  
   ```bash
   git clone https://github.com/Roobiii/ABB_Hackathon.git
   cd ABB_Hackathon
Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows


Install dependencies:

pip install -r requirements.txt


Add your API keys in a .env file:

GROQ_API_KEY=your_groq_api_key_here

▶️ Usage

Run the Streamlit app:

streamlit run app.py


Then open the provided localhost link in your browser.

📊 Example Input

Natural Language:

Turn ON motor when temperature exceeds 50C and pressure is below 100 bar, 
turn OFF when temperature drops below 45C.


Generated IEC 61131-3 Structured Text:

VAR
    Temperature_Sensor : REAL;
    Pressure_Sensor : REAL;
    Motor_Start : BOOL;
END_VAR

IF Temperature_Sensor > 50.0 AND Pressure_Sensor < 100.0 THEN
    Motor_Start := TRUE;
ELSIF Temperature_Sensor < 45.0 THEN
    Motor_Start := FALSE;
END_IF;


Generated Flowchart (Mermaid):

flowchart TD
    A([Start]) --> B{Temperature > 50C AND Pressure < 100 bar?}
    B -- Yes --> C[Turn ON Motor]
    B -- No --> D{Temperature < 45C?}
    D -- Yes --> E[Turn OFF Motor]
    D -- No --> F[Keep Current State]
    C --> F
    E --> F
    F --> G([End])

🧑‍💻 Contributing

Contributions are welcome! Please fork the repo and submit a PR.

📜 License

This project is licensed under the MIT License.


---
