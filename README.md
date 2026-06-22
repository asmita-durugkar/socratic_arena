# Socratic Defense Arena 🎓🤖

An interactive, AI-powered debate platform designed to sharpen critical thinking, logic, and argumentative skills in students. By moving away from passive multiple-choice learning, this platform introduces a dynamic, pressure-tested environment where users must defend their stances against specialized, opposing AI personas.

---

## 🚀 Key Features

### 👥 Dual-Persona AI Architecture
Unlike standard AI tutors, the application utilizes a dual-persona framework to challenge students from multiple cognitive angles:
* **Professor Skeptic:** A sharp, analytical contrarian who ruthlessly checks for logical fallacies, biases, and unverified assumptions in the user's argument.
* **Professor Realist:** A pragmatic evaluator focused on practical, real-world constraints, data, feasibility, and empirical evidence.

### 🌐 Full Multilingual Support (English, Hindi, Marathi)
The platform features an innate language-fluid design driven directly by its advanced LLM backend:
* **Automatic Detection:** Students can type their arguments in **English**, **Hindi (हिन्दी)**, or **Marathi (मराठी)**. The system automatically shifts context and matches the dialogue naturally.
* **Colloquial Support:** Understands "Hinglish" and "Minglish" phonetic text (e.g., typing regional languages using the Latin script), lowering barriers to entry for diverse student groups.
* **Seamless Switching:** Students can shift between languages mid-debate without confusing the AI agents or disrupting the app's state.

### 📊 Real-Time Evaluation
* Provides structured, immediate feedback tracking core metrics: logical structure, empirical grounding, clarity, and tone control.
* Simulates realistic Socratic dialogue inside a clean, intuitive dashboard interface.

---

## 🛠️ Tech Stack

* **Frontend & Application Flow:** Python & Streamlit Cloud
* **Core Logic & Reasoning Backend:** Gemini API
* **State Management:** Streamlit Session States for real-time, fluid turn-based conversational loops

---

## 🏃‍♂️ Local Installation & Setup

Follow these steps to clone and run the project locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/asmita-durugkar/socratic_arena.git
   
   cd socratic_arena
   
3. **Install Dependencies:**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt

4. **Configure Environment Secrets:**
   * **For Local Development:** Create a `.streamlit/secrets.toml` file in your root directory and add your API key:
     ```toml
     GEMINI_API_KEY = "your_api_key_here"
     ```
   * **For Streamlit Cloud Deployment:** Add `GEMINI_API_KEY = "your_api_key_here"` directly under the **Secrets** section in your Streamlit Advanced App Settings dashboard.

5. **Run the Application:**
   ```bash
   streamlit run app.py
   
