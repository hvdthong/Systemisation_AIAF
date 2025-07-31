import pandas as pd

def load_system_context(file_path, sheet_name):
    # Read the specific sheet
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=1)

    # Forward fill the merged cells (QuestionID and Question columns)
    df_raw.iloc[:, 0:2] = df_raw.iloc[:, 0:2].ffill()
    df_raw["QuestionID"] = df_raw["QuestionID"].astype("int64")
    return df_raw

def convert_df_to_system_context_json(df):
    result = {"System Context Question": []}

    # Group by QuestionID and Question text
    grouped = df.groupby(['QuestionID', 'Question'])

    for (question_id, question_text), group in grouped:
        responses = []

        for _, row in group.iterrows():
            # Handle Modifiers as list (optional: enforce numeric)
            modifiers = [float(row['Modifiers'])] if pd.notnull(row['Modifiers']) else []

            responses.append({
                "ResponseID": int(row['ResponseID']),
                "ResponseTitle": row["ResponseTitle"],
                "ResponseDescription": row["ResponseDescription"],
                "Modifiers": modifiers,
                "TagID": row['TagID']
            })

        result["System Context Question"].append({
            "QuestionID": question_id,
            "QuestionText": question_text,
            "Responses": responses
        })

    return result

def load_tags_taxonomy(file_path, sheet_name):
    # Read the specific sheet
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
    return df_raw

def load_risk_area(file_path, sheet_name):
    # Read the specific sheet
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
    return df_raw

def load_focus_question(file_path, sheet_name):
    # Read the specific sheet
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
    return df_raw

def load_risk(file_path, sheet_name):
    # Read the specific sheet
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
    return df_raw

def load_treatment(file_path, sheet_name):
    # Read the specific sheet
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
    return df_raw

def load_focus_question(file_path, sheet_name):
    # Read the specific sheet
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
    return df_raw

def load_requirement(file_path, sheet_name):
    # Read the specific sheet
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
    return df_raw

def load_focus_area(file_path, sheet_name): 
    # Skip the first four rows 
    df = pd.read_excel(file_path, sheet_name, header=None, skiprows=4)
    
    # create the column names 
    df.columns = ["FocusAreaID", "Title", "Description", "TagID", 
                  "Human, Societal, Environmental wellbeing", "Human-centred Value", 
                  "Fairness", "Privacy and Safety",
                  "Reliability and Security", "Transparency and Explainability", 
                  "Contestability", "Accountability"]
    
    bool_cols = df.columns[4:]  # Assuming 5th column onward are boolean flags
    df[bool_cols] = df[bool_cols].applymap(lambda x: True if x == 1 else False)
    df = df.iloc[:14]  # remove the comments 
    return df 