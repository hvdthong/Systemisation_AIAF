import streamlit as st
from load_file import load_system_context, load_focus_question
import pandas as pd 

def get_risk_level(score):
    if score < 13:
        return "Low"
    elif score < 18:
        return "Medium"
    elif score < 22:
        return "High"
    else:
        return "Very High"

def generate_focus_questions(risk_level):
    if risk_level == "Low":
        return []
    elif risk_level == "Medium":
        return ["Baseline"]
    elif risk_level == "High":
        return ["Baseline", "Additional"]
    elif risk_level == "Very High":
        return ["Baseline", "Additional", "SME"]
    return []

# Sample risk-treatment mapping
risk_treatment_data = pd.DataFrame([
    {"RiskID": "R001", "Risk Description": "Data is not encrypted", "TagID": "T001", "Treatment Suggestion": "Implement encryption-at-rest and in-transit"},
    {"RiskID": "R002", "Risk Description": "Facial recognition used without consent", "TagID": "T002", "Treatment Suggestion": "Apply biometric data handling policy & obtain user consent"},
    {"RiskID": "R003", "Risk Description": "No human review of AI outputs", "TagID": "T003", "Treatment Suggestion": "Introduce manual review checkpoint"},
    {"RiskID": "R005", "Risk Description": "Public results not validated", "TagID": "T005", "Treatment Suggestion": "Set up pre-release validation/testing steps"}
])

file_path = 'synthetic_data.xlsx'
sheet_name = 'System Context Assessment' 
df_context = load_system_context(file_path=file_path, sheet_name=sheet_name)

sheet_name = 'Focus Question'
df_focus_question = load_focus_question(file_path=file_path, sheet_name=sheet_name)

# Group by QuestionID
grouped = df_context.groupby("QuestionID")

st.title("NSW AIAF - Risk Assessment")

# Input User Case 
use_case_description = st.text_area("📝 Please fill in your use case")

# Show the Run button to proceed to assessment
if 'show_questions' not in st.session_state:
    st.session_state.show_questions = False

if st.button("Run Assessment"):
    if use_case_description.strip() == "":
        st.warning("⚠️ Please enter your use case before proceeding.")
    else:
        st.session_state.show_questions = True

# Step 2: Display Questions and Collect Responses
if st.session_state.show_questions:

    st.subheader("📋 System Context Questions")

    if 'responses' not in st.session_state:
        st.session_state.responses = {}

    for question_id, group in grouped:
        question_text = group["Question"].iloc[0]
        response_titles = group["ResponseTitle"].tolist()

        st.markdown(f"**Q{question_id}: {question_text}**")

        selected = st.selectbox(
            f"Select your response for Q{question_id}",
            options=response_titles,
            key=f"q_{question_id}"
        )

        selected_row = group[group["ResponseTitle"] == selected].iloc[0]
        st.session_state.responses[question_id] = {
            "question": question_text,
            "selected_response": selected,
            "description": selected_row["ResponseDescription"],
            "modifier": selected_row["Modifiers"],
            "tag": selected_row["TagID"]
        }

    # Step 3: Submit Responses
    if st.button("Submit Responses"):
        st.success("✅ Assessment Results Submitted!")
        st.write("### 📝 Use Case")
        st.write(use_case_description)

        total_modifier = sum(info['modifier'] for info in st.session_state.responses.values())
        base_score = 10
        phase_modifier = 1.3  # You can make this a user input too if needed

        final_risk_score = (base_score + total_modifier) * phase_modifier
        risk_level = get_risk_level(final_risk_score)

        # Store for next step
        st.session_state.risk_level = risk_level
        st.session_state.final_risk_score = final_risk_score

        st.write("### 🔐 Risk Score Calculation")
        st.markdown(f"🎯 **Risk Level:** `{risk_level}`")

        st.write("### ✅ Selected Responses")
        for qid, info in st.session_state.responses.items():
            st.markdown(f"**Q{qid}: {info['question']}**")
            st.markdown(f"• **Selected Response:** {info['selected_response']}")
            st.markdown(f"• _Description:_ {info['description']}")
            st.markdown("---")

    # Step 4: Generate Focus Questions
    if 'risk_level' in st.session_state and st.button("Generate Focus Questions"):
        st.session_state.show_focus_questions = True
        if 'sampled_focus_questions' not in st.session_state:
            st.session_state.sampled_focus_questions = df_focus_question.sample(n=3, random_state=42)
        if 'focus_answers' not in st.session_state:
            st.session_state.focus_answers = {}

    # Step 4 continued: Show checkbox inside a form to avoid reruns on each click
    if st.session_state.get("show_focus_questions", False):
        st.write("### 📝 Use Case")
        st.write(use_case_description)
        st.write("### 🔐 Risk Score Calculation")
        st.markdown(f"🎯 **Risk Level:** `{st.session_state.risk_level}`")

        if df_focus_question.empty:
            st.warning("⚠️ No focus questions available in the dataset.")
        else:
            st.success("📌 Focus Questions Generated")
            st.markdown("### 🧩 Focus Questions to Answer:")

            with st.form("focus_form"):
                focus_answers_temp = {}
                for i, row in st.session_state.sampled_focus_questions.iterrows():
                    key = f"focus_q_{row['FocusQuestionID']}"
                    checked = st.checkbox(row['QuestionText'], key=key)
                    focus_answers_temp[row['FocusQuestionID']] = {
                        "question": row['QuestionText'],
                        "answer": "Yes" if checked else "No",
                        "risk": row.get("RiskID", "N/A"),
                        "tag": row.get("TagID", "N/A")
                    }

                submit_focus = st.form_submit_button("Submit Focus Question Responses")

            if submit_focus:
                st.session_state.focus_answers = focus_answers_temp
                unanswered = [v for v in st.session_state.focus_answers.values() if v['answer'] == "No"]

                if unanswered:
                    st.success("✅ Focus Question Responses Submitted!")
                    st.markdown("### 🛡️ Risks & Suggested Treatments for Answered 'No'")
                    st.table(pd.DataFrame(risk_treatment_data[["Risk Description", "Treatment Suggestion"]]))
                else:
                    st.markdown("✅ All focus questions were marked as 'Yes'. No new risks identified.")
