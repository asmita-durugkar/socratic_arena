import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. PAGE SETUP & API CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Socratic Defense Arena",
    page_icon="🎓",
    layout="centered"
)

# Fetch API key securely from Streamlit Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("🔑 API Key not found! Please configure GEMINI_API_KEY in your secrets.")
    st.stop()

# ==========================================
# 2. PRESET DEBATE TRACKS & TOPICS DATA
# ==========================================
DEBATE_TRACKS = {
    "🚀 Technology & AI": [
        "AI chatbots do more harm than good in modern classrooms.",
        "Social media algorithms should be legally regulated to protect attention spans.",
        "Artificial Intelligence will create far more career opportunities than it destroys."
    ],
    "⚖️ Ethics & Society": [
        "A formal college degree is no longer a requirement for true financial success.",
        "Universal Basic Income is absolutely necessary in an automated economy.",
        "Slowing economic growth is a fair price to pay to stop global climate change."
    ],
    "🎓 Education & Competitions": [
        "Traditional examinations completely fail to measure a student's actual intelligence.",
        "Public speaking and debate training should be mandatory core subjects in every college.",
        "Remote or online learning is fundamentally less effective than in-person classroom education."
    ]
}

# ==========================================
# 3. SYSTEM PROMPTS (THE CORE BRAINS)
# ==========================================

PROFESSOR_SKEPTIC_PROMPT = """
You are Professor Skeptic, a brilliant, ruthlessly sharp academic contrarian. Your job is to audit the student's stance using the classic Socratic method.
- Target cognitive biases, logical fallacies (circular reasoning, ad hominem, strawman), and unverified assumptions.
- Respond dynamically in the SAME language the student uses (English, Hindi, Marathi, or Hinglish/Minglish). Keep your language natural yet intellectually challenging.
- Keep responses concise (under 80 words) and end with one sharp, probing question.

CRITICAL DISMISSAL SYSTEM:
Evaluate the student's argument trajectory closely. You must strictly append one of these tags to the absolute end of your response if conditions are met:
1. If the student has defended their stance logically and robustly for at least 2 rounds, append: [DEBATE_STATUS: SUCCESS]
2. If the student's arguments are circular, unstructured, or failing to make sense after 3 rounds, append: [DEBATE_STATUS: TERMINATE]
Otherwise, do not add any tags.
"""

PROFESSOR_REALIST_PROMPT = """
You are Professor Realist, a pragmatic, data-driven academic evaluator. Your job is to challenge the student's stance using real-world constraints.
- Push back using empirical evidence, practical implementation challenges, economic feasibility, and historical data boundaries.
- Respond dynamically in the SAME language the student uses (English, Hindi, Marathi, or Hinglish/Minglish). Keep your language realistic and challenging.
- Keep responses concise (under 80 words) and end with one sharp, probing question.

CRITICAL DISMISSAL SYSTEM:
Evaluate the student's argument trajectory closely. You must strictly append one of these tags to the absolute end of your response if conditions are met:
1. If the student has defended their stance logically and robustly for at least 2 rounds, append: [DEBATE_STATUS: SUCCESS]
2. If the student's arguments are circular, unstructured, or failing to make sense after 3 rounds, append: [DEBATE_STATUS: TERMINATE]
Otherwise, do not add any tags.
"""

AI_JUDGE_PROMPT = """
You are the Impartial AI Judge. Your task is to analyze the complete transcript of the Socratic debate and output a detailed, structured performance scorecard.
Evaluate the student objectively across these three metrics on a scale of 1-10:
1. **Logical Structure:** Did they maintain a consistent thesis and avoid basic fallacies?
2. **Empirical Grounding:** Did they attempt to back up claims with solid reasoning, facts, or data boundaries?
3. **Clarity & Articulation Mastery:** Evaluate how well they structured sentences under pressure. Point out where they fumbled or lost structural focus, and explain how this preparation helps them shed anxiety for college presentations and placement interviews.

Format your output beautifully using clear Markdown headings, bullet points, and high-impact blockquotes. Be constructive but honest.
"""

# ==========================================
# 4. SESSION STATE MANAGEMENT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0
if "debate_over" not in st.session_state:
    st.session_state.debate_over = False
if "debate_started" not in st.session_state:
    st.session_state.debate_started = False
if "termination_type" not in st.session_state:
    st.session_state.termination_type = None

# ==========================================
# 5. HELPER FUNCTIONS
# ==========================================
def get_llm_response(system_prompt, conversation_history):
    """Orchestrates native Gemini API model generation with specific system contexts."""
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt
        )
        response = model.generate_content(conversation_history)
        return response.text
    except Exception:
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=system_prompt
            )
            response = model.generate_content(conversation_history)
            return response.text
        except Exception as e:
            return f"⚠️ Connection error: {str(e)}. Please click submit again."

def build_raw_transcript():
    """Compiles clean conversational logs for the isolated AI Judge pipeline."""
    transcript = ""
    for msg in st.session_state.messages:
        role_label = "Student" if msg["role"] == "user" else msg["agent_name"]
        transcript += f"{role_label}: {msg['content']}\n\n"
    return transcript

# ==========================================
# 6. SIDEBAR TRACK SELECTION CONFIGURATION
# ==========================================
st.sidebar.title("🎯 Choose Your Track")

if not st.session_state.debate_started:
    selected_track = st.sidebar.selectbox("Select a Domain Track:", list(DEBATE_TRACKS.keys()))
    selected_topic = st.sidebar.selectbox("Choose a Premise / Topic:", DEBATE_TRACKS[selected_track])
else:
    # Lock the selections visually when active so changes don't corrupt runtime history
    st.sidebar.info("🔒 Arena active. Selection locked until current simulation resets.")
import random

# ==========================================
# 6.5 SIDEBAR FUN FACTS (NEW)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🧠 Did You Know?")

fun_facts = [
    "The Socratic Method is named after Socrates, who annoyed so many politicians with his questions that he was put on trial!",
    "Thinking and arguing in a second language actually reduces emotional bias and makes you more logical.",
    "The 'Strawman' fallacy—attacking a fake, weaker version of an argument—is the most common mistake made in amateur debates.",
    "Employers consistently rank 'critical thinking' and 'clear articulation' above technical skills in leadership roles.",
    "The Turing Test, proposed in 1950, was originally called the 'Imitation Game'. It was basically a text-based debate to see if a machine could successfully trick a human judge!",
    "Your brain actually releases dopamine when you hear information that confirms what you already believe. This 'Confirmation Bias' makes it physically difficult to change your mind.",
    "In ancient Athens, a water clock called a 'clepsydra' was used to time debates. If you kept talking after the water ran out, your argument was immediately cut off.",
    "The 'Illusion of Explanatory Depth' is a psychological quirk where people believe they fully understand a topic—until they are asked to explain it step-by-step and realize their logic is flawed.",
    "Communication studies show that pausing for just 3 seconds before answering a difficult question makes the audience perceive you as significantly smarter and more confident.",
    "Large Language Models (like the ones powering your twin professors) don't actually 'think' in sentences. They calculate the mathematical probability of the next logical word token at lightning speed.",
    "The most successful debaters don't actually talk faster; they use 'signposting'—clearly numbering their points (First, Second, Third) so the judge's brain can process the structure easier."
]

# Picks a random fact every time the user interacts
st.sidebar.info(random.choice(fun_facts))    
    

# ==========================================
# 7. USER INTERFACE LAYOUT
# ==========================================
st.title("🎓 Socratic Defense Arena")
st.write("Challenge your logic, eliminate fumbling, and build presentation-ready communication confidence.")
st.markdown("---")

# Step 1: Stance Setup Screen
if not st.session_state.debate_started:
    st.subheader("💡 Set Your Stance")
    st.info("You can type your opinion in English, हिन्दी, मराठी, or Hinglish/Minglish!")
    
    # Visual reference to what was chosen in the sidebar track
    st.markdown(f"**Selected Topic:** `{selected_topic}`")
    stance = st.text_area("What is your initial argument or viewpoint on this topic?")
    
    if st.button("🚀 Enter Arena", use_container_width=True):
        if stance.strip():
            st.session_state.debate_started = True
            # Seed state with the chosen topic and user argument
            st.session_state.messages.append({"role": "user", "content": f"Topic: {selected_topic}\nMy Stance: {stance}"})
            st.session_state.turn_count += 1
            
            with st.spinner("Professor Skeptic is analyzing your logic..."):
                initial_history = f"Topic: {selected_topic}\nStudent Opening Stance: {stance}"
                raw_reply = get_llm_response(PROFESSOR_SKEPTIC_PROMPT, initial_history)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "agent_name": "Professor Skeptic", 
                    "avatar": "🕵️‍♂️", 
                    "content": raw_reply
                })
            st.rerun()
        else:
            st.warning("Please type your argument/viewpoint before entering the arena.")

# Step 2: The Active Arena Screen
else:
    # Render historical back-and-forth dialogue using conversational components
    for msg in st.session_state.messages:
        avatar = msg.get("avatar", "👤")
        with st.chat_message(msg["role"], avatar=avatar):
            if msg["role"] != "user":
                st.caption(f"**{msg['agent_name']}**")
            st.write(msg["content"])

    # Active Loop Guard: Accept inputs only if AI has not fired termination flags
    if not st.session_state.debate_over:
        if user_input := st.chat_input("Type your logical defense here..."):
            st.session_state.messages.append({"role": "user", "avatar": "👤", "content": user_input})
            st.session_state.turn_count += 1
            st.rerun()

        # Check if the last message came from the user; trigger alternating professor orchestration
        if st.session_state.messages[-1]["role"] == "user":
            if st.session_state.turn_count % 2 == 0:
                current_professor = "Professor Skeptic"
                current_prompt = PROFESSOR_SKEPTIC_PROMPT
                current_avatar = "🕵️‍♂️"
            else:
                current_professor = "Professor Realist"
                current_prompt = PROFESSOR_REALIST_PROMPT
                current_avatar = "📊"

            with st.chat_message("assistant", avatar=current_avatar):
                st.caption(f"**{current_professor}**")
                with st.spinner(f"{current_professor} is processing your response..."):
                    history_context = build_raw_transcript()
                    raw_reply = get_llm_response(current_prompt, history_context)
                    
                    # Token-Triggered Termination Scanning Logic
                    if "[DEBATE_STATUS: SUCCESS]" in raw_reply:
                        st.session_state.debate_over = True
                        st.session_state.termination_type = "SUCCESS"
                        raw_reply = raw_reply.replace("[DEBATE_STATUS: SUCCESS]", "").strip()
                        
                    elif "[DEBATE_STATUS: TERMINATE]" in raw_reply:
                        st.session_state.debate_over = True
                        st.session_state.termination_type = "TERMINATE"
                        raw_reply = raw_reply.replace("[DEBATE_STATUS: TERMINATE]", "").strip()

                    st.write(raw_reply)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "agent_name": current_professor, 
                        "avatar": current_avatar, 
                        "content": raw_reply
                    })
            
            if st.session_state.debate_over:
                st.rerun()

    # Step 3: Decoupled AI Judge Pipeline Execution
    else:
        st.markdown("---")
        if st.session_state.termination_type == "SUCCESS":
            st.success("🎉 **Debate Concluded!** The professors acknowledge your structural logic. The execution state is locking down.")
        else:
            st.warning("⚠️ **Debate Concluded!** The dialogue is loop-locking or losing structural focus. The loop has been halted.")

        st.subheader("⚖️ Decoupled AI Judge Evaluation Pipeline")
        
        with st.spinner("The AI Judge is reviewing complete session logs against the performance rubric..."):
            full_transcript = build_raw_transcript()
            judge_scorecard = get_llm_response(AI_JUDGE_PROMPT, full_transcript)
            
            st.markdown(judge_scorecard)
            
        # Provide option to restart the arena simulation
        if st.button("🔄 Reset Arena & Start New Match", use_container_width=True):
            st.session_state.clear()
            st.rerun()
