import streamlit as st
import fitz
import google.generativeai as genai
import os, base64
from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

st.set_page_config(page_title="AI Interviewer", page_icon="🎤", layout="wide")
#<<<sidebar>>>
st.sidebar.markdown("### Interview Settings")

job_role = st.sidebar.selectbox(
    "Job Role",
    ["Data Analyst", "Software Engineer", "Product Manager", "Marketing Intern", "Business Analyst", "HR Manager"],
    index=0
)
st.session_state.role = job_role

exp_level = st.sidebar.selectbox(
    "Experience Level",
    ["Fresher", "Intermediate", "Experienced", "Executive"],
    index=0
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"],
    index=0
)

q_types = st.sidebar.multiselect(
    "Question Types",
    ["Technical", "HR", "Behavioral", "Situational", "Case Study"],
    default=["Technical", "HR"]
)

num_q = st.sidebar.slider(
    "Number of Questions",
    min_value=1,
    max_value=20,
    value=10
)

st.markdown("---")
st.caption("AI-generated content may contain inaccuracies. Always verify important info.")
    
    
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("API Key not found")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.5-flash-lite')

# ============= CSS =============
st.markdown("""
<style>
.A-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
}
.A-header h1 { color: white !important; font-size: 42px; margin:0; }
.A-header p { color: #dbeafe !important; font-size: 18px; margin-top:8px; }
.stApp { background: #f0f4f8; }
.tour-title {
    text-align: center;
    color: #1e3a8a;
    font-weight: 800;
    font-size: 22px;
    margin: 20px 0;
}
.interview-card {
    background: white;
    border-radius: 15px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    height: 280px;
}
.interview-card img {
    width: 100%;
    height: 140px;
    object-fit: cover;
    border-radius: 10px;
}
</style>
<div class="A-header">
    <h1>🎤 AI Smart Interviewer</h1>
    <p>Practice with Voice + Get Instant AI Feedback ✨</p>
</div>
""", unsafe_allow_html=True)

if "role" not in st.session_state:
    st.session_state.role = "Data Analyst"
if "questions" not in st.session_state:
    st.session_state.questions = []
    st.session_state.current_q = 0
    st.session_state.last_feedback = ""

# ============= 4 CARDS =============
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="interview-card">
        <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400">
        <p style="font-weight:700;margin-top:10px;">DATA ANALYST</p>
        <p style="font-size:11px;">📊 SQL + EXCEL + POWER BI PACKAGE</p>
    </div>""", unsafe_allow_html=True)
    if st.button("BOOK NOW - Data", key="b1", use_container_width=True):
        st.session_state.role = "Data Analyst"
        st.toast("Selected: Data Analyst")

with col2:
    st.markdown("""
    <div class="interview-card">
        <img src="https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400">
        <p style="font-weight:700;margin-top:10px;">SOFTWARE ENGINEER</p>
        <p style="font-size:11px;">💻 DSA + SYSTEM DESIGN PACKAGE</p>
    </div>""", unsafe_allow_html=True)
    if st.button("BOOK NOW - SDE", key="b2", use_container_width=True):
        st.session_state.role = "Software Engineer"
        st.toast("Selected: Software Engineer")

with col3:
    st.markdown("""
    <div class="interview-card">
        <img src="https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400">
        <p style="font-weight:700;margin-top:10px;">PRODUCT MANAGER</p>
        <p style="font-size:11px;">🚀 STRATEGY + CASE STUDY PACKAGE</p>
    </div>""", unsafe_allow_html=True)
    if st.button("BOOK NOW - PM", key="b3", use_container_width=True):
        st.session_state.role = "Product Manager"
        st.toast("Selected: Product Manager")

with col4:
    st.markdown("""
    <div class="interview-card">
        <img src="https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?w=400">
        <p style="font-weight:700;margin-top:10px;">MARKETING INTERN</p>
        <p style="font-size:11px;">📣 BRANDING + CAMPAIGN PACKAGE</p>
    </div>""", unsafe_allow_html=True)
    if st.button("BOOK NOW - MKT", key="b4", use_container_width=True):
        st.session_state.role = "Marketing Intern"
        st.toast("Selected: Marketing Intern")

st.divider()
st.subheader(f"Selected Role: {st.session_state.role} - Upload Resume to Start")

# ============= logic =============
resume_file = st.file_uploader("📄 Upload Resume PDF", type="pdf")

def extract_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    txt = "".join([p.get_text() for p in doc])
    return txt[:4000]

if resume_file and st.button("🚀 Generate My Interview Plan"):
    resume_text = extract_text(resume_file)
    prompt = f"""
    Role: {job_role}, 
    Experience: {exp_level}, 
    Difficulty: {difficulty},
    Question Types: {', '.join(q_types)},
    Resume: {resume_text},
    Give {num_q} questions one per line for {job_role} as {exp_level} level.
     """
    res = model.generate_content(prompt)
    st.session_state.questions = [q for q in res.text.split('\n') if len(q.strip())>10]
    st.session_state.current_q = 0

if st.session_state.questions:
    q_list = st.session_state.questions[:15]
    if st.session_state.current_q < len(q_list):
        q = q_list[st.session_state.current_q]
        st.markdown(f'<div class="result-card"><b>Q{st.session_state.current_q+1}: {q}</b></div>', unsafe_allow_html=True)
        
        # Audio
        try:
            tts = gTTS(text=q, lang='en')
            mp3 = BytesIO(); tts.write_to_fp(mp3); mp3.seek(0)
            b64 = base64.b64encode(mp3.read()).decode()
            st.markdown(f'<audio controls autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        except: pass

        if st.session_state.last_feedback:
            st.markdown(f'<div class="result-card">{st.session_state.last_feedback}</div>', unsafe_allow_html=True)

        ans = st.text_area("Your Answer:", key=f"ans{st.session_state.current_q}")
        
        c1,c2 = st.columns(2)
        with c1:
            if st.button("Submit & Get Feedback"):
                fb = model.generate_content(f"Role {st.session_state.role} Q {q} Ans {ans} Give Score/10 + feedback").text
                st.session_state.last_feedback = fb
                st.rerun()
        with c2:
            if st.session_state.last_feedback and st.button("Next Question ->"):
                st.session_state.current_q+=1
                st.session_state.last_feedback=""
                st.rerun()
    else:
        st.balloons()
        st.success("Interview Done! 🎉 Take screenshot for submission")
