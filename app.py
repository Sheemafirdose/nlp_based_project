import streamlit as st
from textblob import TextBlob
from PIL import Image
import fitz  # PyMuPDF for PDF text extraction
import docx
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Sentiment Analyzer", page_icon="🎭", layout="centered")

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Load NLP model for embedding comparisons
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# Function to extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read())
    text = "\n".join([page.get_text() for page in doc])
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Function to compare resume and self-introduction
def compare_texts(resume_text, self_intro):
    resume_embedding = model.encode([resume_text])[0]
    intro_embedding = model.encode([self_intro])[0]
    similarity = cosine_similarity([resume_embedding], [intro_embedding])[0][0]
    return similarity

def extract_resume_summary(resume_text, user_input):
    """Extracts a structured summary from resume text and complements it with user input."""
    # Extract name (assumes name is in the first 100 characters)
    name_match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", resume_text[:100])
    name = name_match.group(0) if name_match else "[Your Name]"
    
    # Keep year as a placeholder
    year = "[Year]"
    
    # Extract branch
    branch_match = re.search(r"(?:Bachelor|B\.?Tech|B\.?E\.?) in ([A-Za-z&/\s]+)", resume_text, re.IGNORECASE)
    branch = branch_match.group(1).strip() if branch_match else "[Your Branch]"
    
    # Extract skills dynamically
    skills_section_match = re.search(r"(?:Skills|Technical Skills|Key Skills|Expertise)[:\n](.*?)(?=\n\n|Experience|Projects|Education|$)", resume_text, re.DOTALL | re.IGNORECASE)
    found_skills = skills_section_match.group(1).strip().split(', ') if skills_section_match else []
    found_skills = [skill.strip() for skill in found_skills if skill.strip()]
    
    # Extract projects dynamically
    project_match = re.findall(r"(?:Project:|Worked on|Research on) ([\w\s]+)", resume_text)
    projects = ", ".join(set(project_match)) if project_match else "various projects"
    
    # Create an enhanced self-introduction
    intro = (
        f"Hello! My name is {name}, and I am a {year} student specializing in {branch}. "
        f"I have hands-on experience in projects where I applied my knowledge of {', '.join(found_skills) if found_skills else '[Skills not mentioned]'}. "
        f"My projects include {projects}, and I continuously work on improving my skills in the field."
    )
    
    return intro

# UI Components
st.markdown("<h1 style='text-align:center; color:white;'>🔍 Sentiment Analysis & Resume Check</h1>", unsafe_allow_html=True)

resume_file = st.file_uploader("📂 Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])

st.subheader("Enter your self-introduction or skills:")
text = st.text_area("Type or paste your details here...", height=200)

if st.button("Assess Feedback"):
    if resume_file:
        # Extract text from the uploaded resume
        if resume_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_file)
        else:
            resume_text = extract_text_from_docx(resume_file)
        
        # Generate Suggested Self-Intro (Improved)
        suggested_intro = extract_resume_summary(resume_text, text)
    elif text.strip():
        # If no resume uploaded, use user input as fallback
        suggested_intro = text.strip()
    else:
        st.warning("⚠️ Please enter some text or upload a resume before analyzing.")
        suggested_intro = ""
    
    if suggested_intro:
        # Store results
        st.session_state.history.append(
            {'text': suggested_intro, 'sentiment': "Suggested Self-Introduction ✨", 'scaled_score': "-", 'suggestion': "This introduction better reflects your resume.", 'color': "skyblue"}
        )
    
    if text.strip():
        sentiment_score = TextBlob(text).sentiment.polarity
        scaled_score = 30 + ((sentiment_score + 1) / 2) * 68
        
        if sentiment_score > 0.5:
            sentiment = "Strongly Positive 😊"
            color = "green"
            suggestion = "Keep up the positive attitude and keep growing!"
        elif sentiment_score > 0:
            sentiment = "Positive 🙂"
            color = "lightgreen"
            suggestion = "Great! Keep nurturing your passion."
        elif sentiment_score < -0.5:
            sentiment = "Strongly Negative 😞"
            color = "red"
            suggestion = "Consider focusing on improvement and confidence-building."
        elif sentiment_score < 0:
            sentiment = "Negative 🙁"
            color = "lightcoral"
            suggestion = "It might help to highlight strengths more clearly."
        else:
            sentiment = "Neutral 😐"
            color = "lightsteelblue"
            suggestion = "Try adding more details or enthusiasm to your introduction."

        st.session_state.history.append({'text': text, 'sentiment': sentiment, 'scaled_score': round(scaled_score, 2), 'suggestion': suggestion, 'color': color})
    
    else:
        st.warning("⚠️ Please enter some text before analyzing.")

# Display Results
for entry in st.session_state.history:
    st.markdown(f"<h3 style='color:{entry['color']};'>{entry['sentiment']}</h3>", unsafe_allow_html=True)
    st.write(f"**Text Entered:** {entry['text']}")
    st.write(f"**Confidence Score:** {entry['scaled_score']}%")
    st.write(f"**Suggestion:** {entry['suggestion']}")
    st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Need help with your introduction or skills?")

with st.expander("How to say a proper intro?"):
    st.write("A proper intro should include who you are, what you do, and your goals. Here's a sample:")
    st.markdown("<p style='font-size:18px; color:white;'>"
                "'Hello! My name is [Your Name], and I am deeply passionate about [Your Field], particularly in the areas of [specific interest within the field]. Currently, I am honing my skills in [Skills/Technologies], and I am excited to apply my knowledge in [specific applications or industries]. My ultimate goal is to contribute to [specific goal or impact], and I am eager to continue growing and collaborating with like-minded professionals.'</p>", unsafe_allow_html=True)

with st.expander("What skills should you build?"):
    st.write("Here are some key skills to build depending on your career goals:")
    st.write("- **For AI/ML**: Python, TensorFlow, Data Science, Machine Learning Algorithms, Deep Learning")
    st.write("- **For Data Science**: Python, R, SQL, Statistics, Data Visualization, Machine Learning")
    st.write("- **For Web Development**: HTML, CSS, JavaScript, React, Node.js")
    st.write("- **For Cloud Computing**: AWS, Azure, Google Cloud, Docker, Kubernetes")
    st.write("- **For Cybersecurity**: Network Security, Ethical Hacking, Cryptography, Risk Management")
    st.write("- **For Mobile Development**: Java, Swift, Android Studio, Flutter")
    st.write("- **For Soft Skills**: Communication, Teamwork, Problem-Solving, Critical Thinking")
    st.write("Search for more specific skills related to your interests and role!")
    st.markdown("[Search for more on YouTube](https://www.youtube.com/)  \n[Explore on ChatGPT](https://chat.openai.com/)  \n[Check Tutorials on GeeksforGeeks](https://www.geeksforgeeks.org/)")

with st.expander("Suggested Videos for Career Growth and Motivation"):
    st.write("Check out these videos to inspire your career journey and decision-making:")
    
    st.markdown(""" 
    - **[How to Choose the Right Career Path | Best Advice](https://youtu.be/h-NjW4Wupzs?si=efERJ69321495G1S)**
    - **[The Psychology of Success | Stay Motivated and Focused](https://youtu.be/8ZhoeSaPF-k?si=Dq2ep-e4T43tQ2C5)**
    - **[Time Management & Productivity Hacks for Students](https://youtu.be/JmOBM160jZ0?si=lNUBI5xk0I99U9rw)**
    """)

    st.write("Want to explore more videos?")
    st.markdown("[Search for more on YouTube](https://www.youtube.com/results?search_query=career+motivation+success+tips)  \n[Google Chrome Search](https://www.google.com/)") 