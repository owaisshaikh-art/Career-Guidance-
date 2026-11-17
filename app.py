import streamlit as st
from dotenv import load_dotenv

from career_engine import generate_rule_based_plan
from llm_service import generate_ai_plan
from utils import make_download

load_dotenv()


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="AI Student Career Guidance Assistant",
    page_icon="🎓",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
:root{--navy:#10243A;--navy2:#173B5E;--teal:#168C8C;--ink:#203247;--muted:#68798B;--paper:#F4F6F8;--line:#DCE4EA}
.stApp{background:var(--paper);color:var(--ink);font-family:'DM Sans',sans-serif}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.block-container{max-width:1380px;padding:1.8rem 3rem 3rem}
h1,h2,h3,h4{color:var(--navy)!important;font-family:'Manrope',sans-serif!important;letter-spacing:-.35px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0B1C2D 0%,#173B5E 100%)}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]{color:#F5F8FB!important}
[data-testid="stSidebar"] [data-testid="stAlert"]{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.18)}
[data-testid="stSidebar"] [data-testid="stAlert"] *{color:#F5F8FB!important}
.career-hero{position:relative;overflow:hidden;padding:34px 38px;border-radius:22px;background:linear-gradient(115deg,#0B1C2D 0%,#173B5E 68%,#176C78 100%);box-shadow:0 14px 34px rgba(16,36,58,.16);margin:0 0 26px}
.career-kicker{color:#8ED7D2!important;font-size:.75rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px}
.career-hero h1{color:#fff!important;font-size:clamp(1.7rem,3vw,2.55rem);font-weight:800;line-height:1.18;margin:0 0 10px}
.career-hero p{color:#E2EDF4!important;font-size:1rem;max-width:780px;line-height:1.65;margin:0}
[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:18px;padding:24px 26px 20px;box-shadow:0 7px 22px rgba(16,36,58,.045)}
.stTextInput input,.stTextArea textarea,.stNumberInput input{background:#fff!important;color:var(--ink)!important;border:1px solid #CBD6DF!important;border-radius:10px!important}
.stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus{border-color:var(--teal)!important;box-shadow:0 0 0 2px rgba(22,140,140,.12)!important}
.stSelectbox [data-baseweb="select"]>div{background:#fff!important;color:var(--ink)!important;border:1px solid #CBD6DF!important;border-radius:10px!important}
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{background:var(--navy)!important;color:#fff!important;border:1px solid var(--navy)!important;border-radius:10px!important;min-height:43px;font-weight:700!important;transition:.18s ease}
.stButton>button:hover,.stFormSubmitButton>button:hover,.stDownloadButton>button:hover{background:var(--teal)!important;border-color:var(--teal)!important;transform:translateY(-1px);box-shadow:0 6px 15px rgba(22,140,140,.18)}
.stButton>button *,.stFormSubmitButton>button *,.stDownloadButton>button *{color:#fff!important}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-top:3px solid var(--teal);border-radius:14px;padding:16px 18px;box-shadow:0 5px 16px rgba(16,36,58,.04)}
[data-testid="stMetricLabel"]{color:var(--muted)!important}
[data-testid="stMetricValue"]{color:var(--navy)!important;font-weight:800!important}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line);border-radius:13px;overflow:hidden}
[data-testid="stExpander"] summary{color:var(--navy)!important;font-weight:700}
[data-testid="stFileUploader"]{background:#fff;border:1.5px dashed #A9BAC8;border-radius:13px;padding:12px}
[data-testid="stAlert"]{border-radius:12px}
[data-testid="stCaptionContainer"]{color:var(--muted)!important}
hr{border-color:var(--line)}
@media(max-width:900px){.block-container{padding:1rem 1rem 2rem}.career-hero{padding:26px 22px}[data-testid="stForm"]{padding:16px}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="career-hero">
  <div class="career-kicker">STUDENT DEVELOPMENT • CAREER INTELLIGENCE</div>
  <h1>CareerPath AI</h1>
  <p>Turn your academic background, strengths and interests into a practical career direction,
  skill-development plan and structured learning roadmap.</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# IMPORTANT:
# - The form key below is "student_profile_form".
# - The profile data key is "student_profile_data".
# These names must remain different.
# --------------------------------------------------
if "career_plan" not in st.session_state:
    st.session_state["career_plan"] = None

if "student_profile_data" not in st.session_state:
    st.session_state["student_profile_data"] = None

if "generation_mode" not in st.session_state:
    st.session_state["generation_mode"] = ""

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.header("About this project")
    st.write(
        "This assistant uses a curated career knowledge base and, when configured, "
        "Groq-powered generative AI to create a personalized career plan."
    )
    st.info("Your profile is used only to generate guidance in this session.")

# --------------------------------------------------
# SAMPLE PROFILES
# --------------------------------------------------
SAMPLE_PROFILES = {
    "B.Com — Finance": {
        "qualification": "Undergraduate",
        "department": "Commerce",
        "degree": "B.Com",
        "year": "Final year",
        "skills": "Excel, accounting basics, communication",
        "interests": "financial markets, budgeting, analysis",
        "industry": "Banking and Financial Services",
        "goal": "Become a financial analyst",
        "location": "India",
    },
    "Mechanical — Automobiles": {
        "qualification": "Undergraduate",
        "department": "Mechanical Engineering",
        "degree": "B.E./B.Tech",
        "year": "Third year",
        "skills": "CAD basics, engineering drawing, teamwork",
        "interests": "automobiles, electric vehicles, design",
        "industry": "Automotive and Mobility",
        "goal": "Work as an automotive design engineer",
        "location": "India",
    },
    "Computer Science — AI": {
        "qualification": "Undergraduate",
        "department": "Computer Science",
        "degree": "B.E./B.Tech",
        "year": "Final year",
        "skills": "Python, SQL, basic statistics",
        "interests": "artificial intelligence, machine learning, automation",
        "industry": "Information Technology",
        "goal": "Become an AI/ML engineer",
        "location": "India",
    },
    "MBA — Business Analytics": {
        "qualification": "Postgraduate",
        "department": "Management",
        "degree": "MBA",
        "year": "Completed",
        "skills": "Excel, presentation, business communication",
        "interests": "business strategy, data, problem solving",
        "industry": "Consulting and Business Services",
        "goal": "Become a business analyst",
        "location": "India",
    },
}

# --------------------------------------------------
# STUDENT PROFILE FORM
# The form key is intentionally NOT "student_profile_data".
# --------------------------------------------------
with st.form("student_profile_form"):
    st.subheader("1. Student profile")
    st.caption("Fields marked * are required. Enter a few words or items separated by commas where indicated.")

    sample = st.selectbox(
        "Load a sample profile (optional)",
        ["Custom profile"] + list(SAMPLE_PROFILES.keys()),
    )
    sample_data = SAMPLE_PROFILES.get(sample, {})

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Name (optional)", placeholder="Your name")

        qualification_options = [
            "Undergraduate",
            "Postgraduate",
            "Diploma",
            "12th / Higher Secondary",
            "Other",
        ]
        qualification_default = sample_data.get("qualification", "Undergraduate")
        qualification = st.selectbox(
            "Qualification",
            qualification_options,
            index=qualification_options.index(qualification_default),
        )

        department = st.text_input(
            "Department / stream *",
            value=sample_data.get("department", ""),
            placeholder="e.g. Computer Science, Commerce, Mechanical Engineering",
        )
        degree = st.text_input(
            "Degree / course",
            value=sample_data.get("degree", ""),
            placeholder="e.g. B.E. Computer Engineering, B.Com, MBA",
        )

        year_options = [
            "First year",
            "Second year",
            "Third year",
            "Final year",
            "Completed",
            "Working professional",
        ]
        year_default = sample_data.get("year", "Final year")
        year = st.selectbox(
            "Current study status",
            year_options,
            index=year_options.index(year_default),
        )

    with col2:
        skills = st.text_area(
            "Current skills * (comma-separated)",
            value=sample_data.get("skills", ""),
            placeholder="e.g. Python, Excel, communication",
            help="List skills you already have. Separate each skill with a comma.",
        )
        interests = st.text_area(
            "Interests * (comma-separated)",
            value=sample_data.get("interests", ""),
            placeholder="e.g. data analysis, finance, designing",
            help="List subjects or activities you enjoy. Separate each with a comma.",
        )

        industry_options = [
            "Not sure yet",
            "Information Technology",
            "Banking and Financial Services",
            "Automotive and Mobility",
            "Healthcare",
            "Education",
            "Manufacturing",
            "Consulting and Business Services",
            "Media and Design",
            "Government / Public Sector",
            "Other",
        ]
        industry_default = sample_data.get("industry", "Not sure yet")
        industry = st.selectbox(
            "Preferred industry",
            industry_options,
            index=industry_options.index(industry_default),
        )

        goal = st.text_input(
            "Career goal *",
            value=sample_data.get("goal", ""),
            placeholder="e.g. Become a data analyst",
            help="Describe the job or career you would like to pursue.",
        )
        location = st.text_input(
            "Preferred job location",
            value=sample_data.get("location", "India"),
            placeholder="e.g. Mumbai, India or Remote",
        )

    submitted = st.form_submit_button(
        "✨ Generate Career Plan",
        type="primary",
        use_container_width=True,
    )

# --------------------------------------------------
# GENERATE CAREER PLAN
# --------------------------------------------------
if submitted:
    if (
        not department.strip()
        or not skills.strip()
        or not interests.strip()
        or not goal.strip()
    ):
        st.error(
            "Please fill in all required fields marked *: Department / stream, Current skills, Interests and Career goal."
        )
    else:
        profile = {
            "name": name.strip(),
            "qualification": qualification,
            "department": department.strip(),
            "degree": degree.strip(),
            "year": year,
            "skills": [x.strip() for x in skills.split(",") if x.strip()],
            "interests": [x.strip() for x in interests.split(",") if x.strip()],
            "industry": industry,
            "goal": goal.strip(),
            "location": location.strip() or "Not specified",
        }

        try:
            with st.spinner("Analyzing your profile and preparing your career plan..."):
                plan, mode = generate_ai_plan(profile)

                if plan is None:
                    plan = generate_rule_based_plan(profile)
                    mode = "Knowledge-base mode"

            # Store the result in application data keys, not widget keys.
            st.session_state["career_plan"] = plan
            st.session_state["student_profile_data"] = profile
            st.session_state["generation_mode"] = mode

            st.success("Career plan generated successfully.")

        except Exception as exc:
            st.error(f"Career plan generation failed: {exc}")

# --------------------------------------------------
# DISPLAY CAREER PLAN
# --------------------------------------------------
plan = st.session_state.get("career_plan")
profile = st.session_state.get("student_profile_data")

if plan is not None and profile is not None:
    st.divider()

    student_name = profile.get("name", "")
    heading = "2. Career plan"
    if student_name:
        heading += f": {student_name}"
    st.subheader(heading)

    st.caption(
        f"Generated using: {st.session_state.get('generation_mode', 'Career assistant')}"
    )

    summary = plan.get("profile_summary", "")
    if summary:
        st.info(summary)

    # CAREER PATHS
    st.markdown("### Recommended career paths")
    roles = plan.get("career_paths", [])

    if not roles:
        st.warning("No career paths were returned. Please generate the plan again.")

    for i, role in enumerate(roles[:3], start=1):
        with st.expander(
            f"{i}. {role.get('role', 'Career role')}",
            expanded=(i == 1),
        ):
            st.write(role.get("why_it_fits", ""))

            st.markdown("**Typical responsibilities**")
            for item in role.get("responsibilities", []):
                st.write(f"• {item}")

            st.markdown("**Important skills**")
            st.write(
                ", ".join(role.get("required_skills", [])) or "Not specified"
            )

            st.markdown("**Relevant qualifications**")
            st.write(role.get("qualification", ""))

            st.markdown("**Certifications to consider**")
            for item in role.get("certifications", []):
                st.write(f"• {item}")

    # SKILL GAP
    st.markdown("### Skill-gap analysis")
    gaps = plan.get("skill_gap", {})
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Skills you already have**")
        for item in gaps.get("existing_skills", profile.get("skills", [])):
            st.write(f"✅ {item}")

    with col2:
        st.markdown("**Skills to develop**")
        for item in gaps.get("missing_skills", []):
            st.write(f"🎯 {item}")

    for item in gaps.get("actions", []):
        st.write(f"• {item}")

    # LEARNING ROADMAP
    st.markdown("### Learning roadmap")
    for stage in plan.get("roadmap", []):
        with st.expander(
            stage.get("stage", "Learning stage"),
            expanded=True,
        ):
            st.write(f"**Goal:** {stage.get('goal', '')}")
            st.write(f"**Topics:** {', '.join(stage.get('topics', []))}")

            st.markdown("**Practice activities**")
            for item in stage.get("activities", []):
                st.write(f"• {item}")

            st.markdown("**Project idea**")
            st.write(stage.get("project", ""))

    # LEARNING RESOURCES
    st.markdown("### Learning resources")
    for resource in plan.get("learning_resources", []):
        title = resource.get("name", "Learning resource")
        url = resource.get("url", "")
        purpose = resource.get("purpose", "")

        if url.startswith("https://"):
            st.markdown(f"- [{title}]({url}) — {purpose}")
        else:
            st.write(f"- {title} — {purpose}")

    # JOB SEARCH RESOURCES
    st.markdown("### Job-search resources")
    for item in plan.get("job_search_resources", []):
        url = item.get("url", "")
        if url.startswith("https://"):
            st.markdown(
                f"- [{item.get('name', 'Job portal')}]({url}) — "
                f"{item.get('purpose', '')}"
            )

    st.caption(
        "Job portals are provided as search resources. "
        "This application does not claim that any vacancy is live or available."
    )

    # DOWNLOADS
    st.markdown("### Download your career plan")
    download_data = make_download(profile, plan)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "⬇️ Download career plan (JSON)",
            data=download_data,
            file_name="my_career_plan.json",
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "⬇️ Download career plan (PDF)",
            data=make_download(profile, plan, file_format="pdf"),
            file_name="my_career_plan.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

st.divider()
st.markdown(
    """
    <div style="text-align:center;padding:12px 0 4px">
      <div style="color:#173B5E;font-weight:800;font-family:Manrope,sans-serif">CAREERPATH AI</div>
      <div style="color:#68798B;font-size:.82rem;margin-top:6px">
        Career guidance is informational, not a guarantee of employment or admission.
        Verify current course details, fees, eligibility and certification status on official provider websites.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
