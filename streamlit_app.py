import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
import docx  # for docx file reading
import requests  # for calling the LLaMA API

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    with fitz.open(pdf_file) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

# Function to extract text from Word document
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

# Function to generate chatbot responses from LLaMA
def get_llama_response(user_input, cv_text, conversation_history):
    url = "https://your-llama-api-endpoint.com/v1/generate"  # Replace with actual LLaMA API endpoint
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",  # Replace with your LLaMA API key if needed
        "Content-Type": "application/json"
    }
    
    # Creating the payload with CV text, previous conversation, and user query
    prompt = f"Based on the following CV details: {cv_text}\n\nInterview conversation history: {conversation_history}\n\nNext Question:"
    payload = {
        "input": prompt,
        "parameters": {
            "max_tokens": 150,
            "temperature": 0.7
        }
    }
    
    # Sending request to the LLaMA API
    response = requests.post(url, json=payload, headers=headers)
    
    # Handling response from LLaMA
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('generated_text', 'No response from LLaMA')
    else:
        return "Error in fetching response from LLaMA."

# Streamlit app setup
st.title("CV-based Full-Fledged Interview Chatbot")

# Allow user to upload CV
uploaded_file = st.file_uploader("Upload your CV (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    # Extract text from the uploaded file
    if uploaded_file.type == "application/pdf":
        cv_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        cv_text = extract_text_from_docx(uploaded_file)
    
    st.write("CV Text Extracted Successfully!")
    
    # Initialize session state for conversation history if not already present
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = ""
    
    # Show extracted CV text (optional, you can choose to hide it)
    st.write("### Extracted CV Text:")
    st.text_area("CV Text", value=cv_text, height=200, disabled=True)

    # Start Interview
    st.write("### Interview Started")
    st.write("The bot will now ask you a series of questions based on your CV. Respond to each question.")
    
    # Chatbot conversation loop
    user_input = st.text_input("Your Answer:")
    
    if user_input:
        # Append the user's answer to the conversation history
        st.session_state.conversation_history += f"\nUser: {user_input}"

        # Get the chatbot's response based on conversation history and CV
        chatbot_response = get_llama_response(user_input, cv_text, st.session_state.conversation_history)
        
        # Show chatbot response
        st.session_state.conversation_history += f"\nChatbot: {chatbot_response}"
        
        st.write(f"**Chatbot's Question:** {chatbot_response}")
    
    # Show the ongoing conversation history
    st.write("### Interview History:")
    st.text_area("Conversation", value=st.session_state.conversation_history, height=300, disabled=True)
