import streamlit as st
from google import genai
from google.genai import types
import json
import random
import re

# ==========================================
# 1. Page Configuration & CSS
# ==========================================
st.set_page_config(
    page_title="Socratic Defense Arena", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .badge-card {
        background-color: #1E1E2E;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #89B4FA;
        text-align: center;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
        transition: transform 0.2s;
        margin-bottom: 15px;
    }
    .badge-card:hover {
        transform: scale(1.02);
    }
    .badge-title {
        color: #CBA6F7;
        font-size: 22px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .badge-desc {
        color: #A6ADC8; 
        margin: 0;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚔️ Socratic Defense Arena")
st.caption("Enter the Arena. Defeat the Professors. Level up your Critical Thinking!")

# 🔑 SECURE API KEY INJECTION (For Streamlit Cloud & Local secrets.toml) 🔑
MY_GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

# ==========================================
# 2. Database (Topics & Trivia)
# ==========================================
TOPIC_CATEGORIES = {
    "🌐 Society & Tech": [
        "Social media does more harm than good for teenagers",
        "AI tools like ChatGPT make students lazy instead of smarter",
        "Video games actively help develop teamwork and strategic thinking"
    ],
    "🧬 Ethics & Life": [
        "Schools should completely ban homework to protect student mental health",
        "Money can buy happiness if spent on experiences rather than items",
        "All public transport inside major cities should be completely free"
    ],
    "🎬 Pop Culture & Influencers": [
        "Social media influencers earn massive amounts of money without doing any real work",
        "Professional athletes are paid way too much money compared to essential workers",
        "Movies are better watched alone at home than inside a crowded cinema"
    ]
}

FUN_FACTS = [
    "The ancient Greeks invented the Socratic method over 2,400 years ago to break down hidden assumptions through questions instead of boring lectures!",
    "In ancient Rome, public live debates were treated like modern sports matches—crowds would pack stadiums to cheer on their favorite speakers.",
    "The word 'Debate' comes from the Old French word 'debatre', which literally translates to 'fight or beat down'—but cleanly with words!",
    "Philosopher Socrates never actually wrote down his ideas. Everything we know about him comes from dialogues recorded by his student, Plato.",
    "The 1960 Kennedy-Nixon debate changed media forever: radio listeners thought Nixon won, but TV viewers chose Kennedy because he looked calmer!",
    "Scientific studies show that participating in structured debates boosts a student's active critical thinking metrics by up to 44% more than standard textbook reading."
]

# ==========================================
# 3. Sidebar Configuration
# ==========================================
with st.sidebar:
    st.header("🎮 Level Select")
    category = st.selectbox("Select Campaign Track", list(TOPIC_CATEGORIES.keys()))
    topic = st.selectbox("Choose Your Mission", TOPIC_CATEGORIES[category])
    start_btn = st.button("🔄 Start New Match", use_container_width=True)
    
    st.write("---")
    
    st.markdown("### 💡 Did You Know?")
    if "current_fact" not in st.session_state or start_btn:
        st.session_state.current_fact = random.choice(FUN_FACTS)
    st.info(st.session_state.current_fact)

# ==========================================
# 4. System Logic & API Connection
# ==========================================
SYSTEM_INSTRUCTION = f"""
You are conducting a friendly but critical academic debate with a student on the topic: '{topic}'.
There are two personas here:
1. Professor Skeptic: Questions assumptions and points out logical flaws.
2. Professor Realist: Asks how the student's idea works out in day-to-day life.

CRITICAL RULES:
- Do NOT demand research papers, scientific journals, or specific data references.
- Accept personal life experiences, logical analogies, common sense, and philosophical reasoning.
- Keep your combined response brief (under 4 sentences total). Take turns naturally.
"""

def get_gemini_client():
    return genai.Client(api_key=MY_GEMINI_KEY)

def call_gemini_with_fallback(client, contents, system_instruction=None, json_mode=False):
    # Testing the most stable, active models
    models_to_try = [
        'gemini-2.5-flash',
        'gemini-2.0-flash', 
        'gemini-1.5-flash-8b',
        'gemini-1.5-flash'
    ] 
    
    config_args = {"temperature": 0.7}
    if system_instruction:
        config_args["system_instruction"] = system_instruction
    if json_mode:
        config_args["response_mime_type"] = "application/json"
        
    config = types.GenerateContentConfig(**config_args)
    
    # We will store ALL errors here so we can see exactly what is blocking us
    error_logs = []
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            error_logs.append(f"[{model_name}]: {str(e)}")
            continue
            
    # If everything fails, print the full list of reasons!
    return "API ERROR LOG:\n" + "\n".join(error_logs)

# ==========================================
# 5. Live Chat State Management
# ==========================================
if "chat_history" not in st.session_state or start_btn:
    st.session_state.chat_history = []
    st.session_state.display_history = []
    st.session_state.exam_finished = False
    
    client = get_gemini_client()
    with st.spinner("⚔️ Professors are drawing their opening cards..."):
        welcome_prompt = f"Welcome the student warmly to the debate arena on '{topic}'. Challenge them to step up and make their first move!"
        initial_greeting = call_gemini_with_fallback(client, welcome_prompt, SYSTEM_INSTRUCTION)
        
        st.session_state.display_history.append({"role": "assistant", "content": initial_greeting})
        st.session_state.chat_history.append(types.Content(role="model", parts=[types.Part.from_text(text=initial_greeting)]))

# Render Live Chat Stream
for msg in st.session_state.display_history:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else None):
        st.write(msg["content"])

# User Input Logic
if not st.session_state.exam_finished:
    if user_input := st.chat_input("Strike back with your argument here..."):
        client = get_gemini_client()
        
        with st.chat_message("user"):
            st.write(user_input)
            
        st.session_state.display_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_input)]))
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Professors are calculating counter-defenses..."):
                ai_reply = call_gemini_with_fallback(client, st.session_state.chat_history, SYSTEM_INSTRUCTION)
                st.write(ai_reply)
                
                st.session_state.display_history.append({"role": "assistant", "content": ai_reply})
                st.session_state.chat_history.append(types.Content(role="model", parts=[types.Part.from_text(text=ai_reply)]))

# ==========================================
# 6. Gamified Analytics Dashboard
# ==========================================
if len(st.session_state.display_history) > 1 and not st.session_state.exam_finished:
    st.write("")
    if st.button("🏆 End Match & Claim Rewards", use_container_width=True):
        st.session_state.exam_finished = True
        client = get_gemini_client()
        
        with st.spinner("🧙‍♂️ The Elder Judges are tallying your experience points..."):
            transcript = ""
            for msg in st.session_state.display_history:
                transcript += f"{msg['role'].upper()}: {msg['content']}\n\n"
            
            judge_prompt = f"""
            Analyze this debate transcript. You must calculate gamified metrics for a student.
            Assign one of these three Titles based on overall performance: "Socratic Knight" (85+), "Logic Squire" (65-84), or "Philosophy Peasant" (<65).
            Assign one Badge out of these based on their best trait: "Shield of Logic", "Silver Tongue", or "Unshakable Mind".
            
            Output raw JSON matching this structure exactly:
            {{
              "logic_score": 85,
              "rhetoric_score": 78,
              "confidence_score": 92,
              "overall_xp": 2550,
              "title": "Logic Squire",
              "badge": "Shield of Logic",
              "superpower": "Great job standing your ground against the Realist.",
              "weakness": "Watch out for emotional traps set by the Skeptic."
            }}
            
            TRANSCRIPT:
            {transcript}
            """
            
            raw_json = call_gemini_with_fallback(client, judge_prompt, json_mode=True)
            
            # Clean the AI output using Regular Expressions
            match = re.search(r'\{.*\}', raw_json, re.DOTALL)
            
            try:
                if match:
                    clean_json_string = match.group(0)
                else:
                    clean_json_string = raw_json 
                    
                data = json.loads(clean_json_string)

                st.balloons()
                st.snow()
                
                st.markdown("## 📊 ARENA MATCH SUMMARY")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="badge-card">
                        <div style="font-size: 45px;">🏆</div>
                        <div class="badge-title">{data.get('title', 'Unranked')}</div>
                        <p class="badge-desc">Your Earned Rank Tier</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="badge-card">
                        <div style="font-size: 45px;">🛡️</div>
                        <div class="badge-title">{data.get('badge', 'Novice')}</div>
                        <p class="badge-desc">Special Attribute Unlocked</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="badge-card">
                        <div style="font-size: 45px;">✨</div>
                        <div class="badge-title">+{data.get('overall_xp', 0)} XP</div>
                        <p class="badge-desc">Total Experience Points Gathered</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write("---")
                st.markdown("### 📈 Core Stat Attributes")
                
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric(label="🧠 Logic Matrix Level", value=f"{data.get('logic_score', 0)}/100")
                with m2:
                    st.metric(label="🗣️ Rhetoric Power Level", value=f"{data.get('rhetoric_score', 0)}/100")
                with m3:
                    st.metric(label="🔋 Emotional Stamina Level", value=f"{data.get('confidence_score', 0)}/100")
                
                st.write("---")
                
                left_box, right_box = st.columns(2)
                with left_box:
                    st.success(f"🔥 Class Superpower Activated:\n\n{data.get('superpower', 'Analysis pending.')}")
                with right_box:
                    st.warning(f"⚠️ Debuff / Vulnerability Spotted:\n\n{data.get('weakness', 'Analysis pending.')}")
                    
            except Exception as parse_error:
                st.error("Dashboard compilation failed. The AI returned an invalid format.")
                st.write("Here is what the AI actually sent back:")
                st.code(raw_json)
