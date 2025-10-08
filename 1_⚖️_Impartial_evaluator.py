import streamlit as st
import pandas as pd
from pandas import read_excel
import joblib
import pathlib
import os
import io
import re
from utils import evaluate_outputs_single_chat

#Function to load CSS from the 'assets' folder
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}<\style>")

#load the external css
css_path = pathlib.Path("assets/styles.css")
load_css(css_path)

#cache file for testing
cache_file = "openai_cache.pkl"

#either loading cache file
if os.path.exists(cache_file):
    response_cache = joblib.load(cache_file)
#or creating an empty one
else:
    response_cache = {}

#api key pattern to match sk- and any number of alphanumeric characters including minus and underscore
api_key_pattern = r"^sk-[A-Za-z0-9_\-]*$"

#create a column layout
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    #Title of the document
    st.markdown("# ⚖️ Impartial Evaluator")
    #Form
    with st.form("api_key_form"):
        api_key = st.text_input(label='Please enter your OpenAI Api Key', type="password", placeholder="sk-...")
        submitted = st.form_submit_button("Submit")

        #if submitted then show a sucess and update session states
        if submitted:
            if re.fullmatch(api_key_pattern, api_key):
                st.success("Valid API key format.")
                st.session_state['api_key'] = api_key
                st.session_state["submitted"] = True
                #error if input does not match regex
            else:
                st.error("Invalid API key format.")
                #form to upload excel file

    with st.form("upload_form"):
        excel_file = st.file_uploader("Upload an excel sheet", type=["xlsx"])
        upload_file = st.form_submit_button("Confirm Upload")
        if excel_file is not None and upload_file:
            try:
                st.success("File uploaded")
                st.session_state["uploaded"] = True
                    #if excel file cannot be read throw an error
            except Exception as e:
                st.error(f"An error occured while reading the file: {e}")
      
    generate_rating = st.button("Generate Rating")

        
#if user clicked on generate rating button, API key and excel file are successfully submitted
    if generate_rating and st.session_state.get("submitted") and st.session_state.get("uploaded"):
        prompt_output_df = read_excel(excel_file)
        prompt_output_dict = dict(zip(prompt_output_df.iloc[:, 0], prompt_output_df.iloc[:, 1]))
        #get rating and potential errors from OpenAI
        rating, error = evaluate_outputs_single_chat(st.session_state.get("api_key"), prompt_output_dict, response_cache, cache_file)
        if error:
            st.warning(f"⚠️ Something went wrong")
        #if rating was genearted, initiate rows for df, file for .txt file and html list for the rendered list
        if rating:
            rows=[]
            file_content = io.StringIO()
            # Save to an in-memory buffer
            buffer = io.BytesIO()

            #create unordered list
            with st.container(border=True):
                html_list = "<ul>"

                #write the unordered list, the .txt file and the rows
                for prompt, outputs in rating.items():
                    html_list += f"<li><b>{prompt}</b><ul>"
                    file_content.write(f"- **{prompt}**\n")

                    for output, criteria in outputs.items():
                        html_list += f"<li>{output}<ul>"
                        file_content.write(f"  - {output}\n")
                        row={"Prompt": prompt, "Output": output}

                        for i, (criterion, score) in enumerate(criteria.items()):
                            html_list += f"<li>{criterion}: {score}</li>"
                            file_content.write(f"    - {criterion}: {score}\n")
                            row[f"Criterion{criterion}"] = criterion
                            row[f"Rating {criterion}"] = score
                        rows.append(row)

                        html_list += "</ul></li>"
                    html_list += "</ul></li>"
                html_list += "</ul>"
                st.markdown(html_list, unsafe_allow_html=True)
                
            #create df out of rows and write .xlsx file
            df = pd.DataFrame(rows)
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="evaluation.xlsx")
                #rewind to the start
                buffer.seek(0)


            with col2:
                horizontal_col1, horizontal_col2 = st.columns(2)

                #download button for .txt file
                with horizontal_col1:
                    st.download_button(
                        label="Download .txt file",
                        data=file_content.getvalue(),
                        file_name="evaluation.txt",
                        mime="text/plain"
                    )
                #download button for excel file
                with horizontal_col2:
                    st.download_button(
                        label="Download .xlsx file",
                        data=buffer,
                        file_name="evaluation.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    elif generate_rating and not st.session_state.get("submitted") and st.session_state.get("uploaded"):
        st.error("Enter a valid Open AI API key to generate ratings")
    elif generate_rating and  st.session_state.get("submitted") and not st.session_state.get("uploaded"):
        st.error("Upload an Excel file to generate ratings")
    elif generate_rating and not st.session_state.get("submitted") and not st.session_state.get("uploaded"):
        st.error("Enter a valid Open AI API key and upload an Excel file to generate ratings")