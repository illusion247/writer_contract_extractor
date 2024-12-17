import streamlit as st
import os
from dotenv import load_dotenv
import io
import re
from writer import WriterClient, Document, File
from writer.models import GenerationRequest

load_dotenv()

# Writer SDK setup
api_key = st.secrets["WRITER_API_KEY"]  # Assumes you have this key in Streamlit secrets
organization_id = st.secrets["WRITER_ORG_ID"]  # Assumes you have this org ID in Streamlit secrets

client = WriterClient(
    api_key=api_key,
    organization_id=organization_id
)

# Function to extract info directly from PDF with Writer SDK
def extract_info_writer(pdf_file):
    if pdf_file:
        prompt = f"""
            Analyze the following contract document and extract the following information:

            1. Termination Notice No. of Days:  How many days are required to give for a termination notice, and indicate which party is terminating the contract.
            2. Auto Renewal: Does the contract contains a renewal clause, if so please include details. Find information that refers to the renewal of contract.
            3. Signed Date of the Client (client): Extract the date signed by the client.
            4. Effectivity Date: find information or clause about the effectivity date of the contract.
            5. Service provider: Willis Towerswatson or Towers Watson entity name involve
            6. Data privacy: Extract information related to Data privacy agreements or clause related
            Additional instructions:
             1. Provide the page number and section number for reference if information is available.
             2. For each of the above, only output the relevant text that was parsed from the document and format the output in the following format using these tags.
                
                  [Service]
                  [results]
                  <b>WTW Entity:</b> <Service provider>
                  [raw extracted]
                 <relevant text from the signature section>
                  [Service]

                [Termination]
                [results]
                <b>Termination Notice No. of Days:</b> <Termination Notice and which party is giving the notice> <br>
                 Section(s): <section number(s)>, Page(s): <page number(s)>
                [raw extracted]
                 <relevant text from the termination section>
                [Termination]

                [Renewal]
                [results]
                 <b>Auto Renewal:</b> <Renewal Clause Details> <br>
                 Section(s): <section number(s)>, Page(s): <page number(s)>
                [raw extracted]
                 <relevant text from the renewal section>
                [Renewal]

                 [Signed Date]
                [results]
                 <b>Signed Date of the Client (<client name>):</b> <Date of the client signing> <br>
                  Section(s): <section number(s)>, Page(s): <page number(s)>
                 [raw extracted]
                 <relevant text from the signature section>
                 [Signed Date]

                 [Effectivity Date]
                  [results]
                  <b>Effectivity Date:</b> <Effectivity Date> <br>
                  Section(s): <section number(s)>, Page(s): <page number(s)>
                  [raw extracted]
                   <relevant text from the Effectivity section>
                  [Effectivity Date]

                  [Data privacy]
                  [results]
                  <b>Data privacy:</b> <Data privacy agreements or clause related> <br>
                  Section(s): <section number(s)>, Page(s): <page number(s)>
                  [raw extracted]
                 <relevant text from the Data privacy section>
                  [Data privacy]

        Note: The Service Provider is always Towers Watson or Willis Towers Watson. Please extract only the Client's Signature Date.
            """
        try:
             pdf_content = pdf_file.read()
             file_data = File(content=pdf_content, file_name = pdf_file.name, mime_type="application/pdf")

             req = GenerationRequest(
                model="premium",
                prompt=prompt,
                files=[file_data]
              )
             response = client.ai.generate(req)
             return response.text
        except Exception as e:
            return f"Error querying Writer API: {e}"
    else:
         return "No file Uploaded"


# Streamlit app
with st.sidebar:
    #st.title("Contract Information Extractor")
    st.header("Contract Information Extractor", divider="gray")
    uploaded_file = st.file_uploader("Upload a Contract PDF", type="pdf")

if uploaded_file:
    with st.spinner("Extracting information..."):
       extracted_data = extract_info_writer(uploaded_file)
       if extracted_data:
          st.success("Information extracted successfully!")

          service_match = re.search(r"\[Service\]\s*\[results\]\s*(.*?)\s*\[raw extracted\]\s*(.*?)\s*\[Service\]", extracted_data, re.DOTALL)
          termination_match = re.search(r"\[Termination\]\s*\[results\]\s*(.*?)\s*\[raw extracted\]\s*(.*?)\s*\[Termination\]", extracted_data, re.DOTALL)
          renewal_match = re.search(r"\[Renewal\]\s*\[results\]\s*(.*?)\s*\[raw extracted\]\s*(.*?)\s*\[Renewal\]", extracted_data, re.DOTALL)
          signed_match = re.search(r"\[Signed Date\]\s*\[results\]\s*(.*?)\s*\[raw extracted\]\s*(.*?)\s*\[Signed Date\]", extracted_data, re.DOTALL)
          effectivity_match = re.search(r"\[Effectivity Date\]\s*\[results\]\s*(.*?)\s*\[raw extracted\]\s*(.*?)\s*\[Effectivity Date\]", extracted_data, re.DOTALL)
          Dataprivacy_match = re.search(r"\[Data privacy\]\s*\[results\]\s*(.*?)\s*\[raw extracted\]\s*(.*?)\s*\[Data privacy\]", extracted_data, re.DOTALL)

          with st.expander("Service Provider", expanded=True):
            if service_match:
              results, raw_text = service_match.groups()
              st.markdown(results.strip(), unsafe_allow_html=True)  # Use markdown for HTML
              st.code(raw_text.strip(), wrap_lines=True)
            else:
              st.write("Not found")  
            
          with st.expander("Signed Date", expanded=True):
                if signed_match:
                  results, raw_text = signed_match.groups()
                  st.markdown(results.strip(), unsafe_allow_html=True)  # Use markdown for HTML
                  st.code(raw_text.strip(), wrap_lines=True)
                else:
                   st.write("Not found")
          with st.expander("Effectivity Date", expanded=True):
               if effectivity_match:
                 results, raw_text = effectivity_match.groups()
                 st.markdown(results.strip(), unsafe_allow_html=True)  # Use markdown for HTML
                 st.code(raw_text.strip(), wrap_lines=True)
               else:
                    st.write("Not found")
          with st.expander("Termination", expanded=True):
                if termination_match:
                  results, raw_text = termination_match.groups()
                  st.markdown(results.strip(), unsafe_allow_html=True) # Use markdown for HTML
                  #radio_markdown = raw_text.strip()
                  #st.markdown("<b><font color=red>Reference</font></b>", help=radio_markdown, unsafe_allow_html=True)
                  st.code(raw_text.strip(), wrap_lines=True)
                else:
                    st.write("Not found")
          with st.expander("Auto Renewal", expanded=True):
                if renewal_match:
                    results, raw_text = renewal_match.groups()
                    st.markdown(results.strip(), unsafe_allow_html=True)  # Use markdown for HTML
                    st.code(raw_text.strip(), wrap_lines=True)
                else:
                    st.write("Not found")

          with st.expander("Data privacy", expanded=True):
                if Dataprivacy_match:
                    results, raw_text = Dataprivacy_match.groups()
                    st.markdown(results.strip(), unsafe_allow_html=True)  # Use markdown for HTML
                    st.code(raw_text.strip(), wrap_lines=True)
                else:
                    st.write("Not found")


       else:
          st.error("Error during information extraction.")