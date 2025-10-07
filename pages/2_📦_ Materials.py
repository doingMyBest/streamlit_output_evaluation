import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

# Load your custom CSS file
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="Materials", layout="wide")
st.title("📦 Materials")

content_container, empty_container = st.columns([1, 2])

with content_container:
    tab_pdf, tab_link = st.tabs(["📄 PDFs", "🔗 Links"])


#use pdf viewer to render pdf
    with tab_pdf:
        pdf_path = "assets/Bewertungsschema_final.pdf"

        st.subheader("Evaluation Questionnaire")
        try:
            pdf_viewer(pdf_path, width="100%", zoom_level=1.0, viewer_align="left", show_page_separator=False)
            #download button below pdf viewer
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name="Evaluation_Questionnaire.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        except Exception as e:
            st.error(f"Unable to embed PDF with `st.pdf`: {e}")

    with tab_link:
    # Store the URLs in a dict
        link_dict = {
            "GitHub Repo": "https://github.com/your‑repo",
            "Preprint":    "https://arxiv.org/abs/2509.26205",
            "Project Website":    "https://papermaker.ai/",
        }   

    # Render each link as a clickable markdown line
        for name, url in link_dict.items():
            st.markdown(f"- [{name}]({url})")