import streamlit as st


st.title("❓ Frequently Asked Questions")

#dict with questions and answers
faq = {
    "What is this app for?": "This app helps you to evaluate textual AI outputs from a human-centered perspective. This means that it evaluates wether the output text is understandable and useful for humans.",
    "How do I upload a file?": "Use the file uploader. Structure your excel spreadsheet (.xlsx) file the following: the first column is the \"input\" (prompt) and the second column is the \"output\" (answer).",
    "Which large language model (LLM) is the impartial evaluator using?": "Currently, the impartial evaluator uses GPT-4o. A model switcher to switch between LLMs is in the making.", 
    "Why do I have to enter my OpenAI API key? Is it safe to enter it?": "You have to enter your API key, for the app to \"talk\" to the large language model (LLM) and retrieve a rating. Your API key is solely used for this purpose and not saved permanently.",
    "Why does the AI not give me ratings for all evaluation metrics?": "The approach is a collaboration between humans and large language models (LLMs). This means that certain metrics are solely evaluated by humans to avoid overreliance. Others are evaluated by the AI but they need human-checking too.",
    "How do I reference this work?": """Please use the following citation:  
    Mangold, A., & Hoffmann, K. (2025). Human‑centered evaluation of RAG outputs:  
        A framework and questionnaire for human‑AI collaboration. arXiv.  
        https://arxiv.org/abs/2509.26205  
        """  
}


#write out the questions and answers in the dict
for q,a in faq.items():
    with st.expander(q):
        st.write(a)