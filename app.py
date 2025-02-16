import streamlit as st
from textblob import TextBlob
from PIL import Image
import fitz  # PyMuPDF for PDF text extraction
import docx
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import ollama


# Set page configuration
st.set_page_config(page_title="Sentiment Analyzer", page_icon="📝", layout="centered")

# Apply custom CSS styles
def load_css():
    st.markdown("""
    <style>
        /* Glowing effect for the expanders */
        .streamlit-expanderHeader {
            color: white;
            border: 2px solid white !important;
            box-shadow: 0px 0px 15px white !important;
            padding: 5px 15px;
            border-radius: 10px;
        }

        .streamlit-expanderContent {
            background-color: #333;  /* Optional: Dark background for contrast */
            border: 2px solid white !important;
            box-shadow: 0px 0px 15px white !important;
            padding: 10px;
            border-radius: 10px;
        }

        /* For the input box and button (to ensure white glowing effect is consistent) */
        textarea {
            border: 2px solid white !important;
            box-shadow: 0px 0px 15px white !important;
            border-radius: 10px;
        }

        .stButton > button {
            border: 2px solid white !important;
            box-shadow: 0px 0px 15px white !important;
            padding: 10px;
            border-radius: 10px;
            display: block;
            margin: 0 auto;  /* Center the button */
        }

        /* For the additional box (with the glowing effect) */
        .additional-box {
            border: 2px solid white !important;
            box-shadow: 0px 0px 15px white !important;
            background-color: #333;  /* Dark background for contrast */
            padding: 15px;
            border-radius: 10px;
        }

        /* For additional box sections */
        .stMarkdown {
            color: white;  /* Ensure text inside is white */
        }

        .st-expander {
            border: 2px solid white !important;
            box-shadow: 0px 0px 15px white !important;
            background-color: #333;
            padding: 10px;
            border-radius: 10px;
        }

        a {
            color: #00b0f0;  /* Light blue color for links */
            text-decoration: none;
        }

        a:hover {
            color: #ffffff;
            text-decoration: underline;
        }
    </style>
    """, unsafe_allow_html=True)

# Load styles
load_css()

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Load NLP model for embedding comparisons
if "st_model" not in st.session_state:
    st.session_state.st_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
model = st.session_state.st_model

# Function to extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
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

# Function to extract structured summary from resume using Ollama
def extract_resume_summary(resume_text):
    name_match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", resume_text[:100])
    name = name_match.group(0) if name_match else "[Your Name]"

    branch_match = re.search(r"(?:Bachelor|B\.?Tech|B\.?E\.?) in ([A-Za-z&/\s]+)", resume_text, re.IGNORECASE)
    branch = branch_match.group(1).strip() if branch_match else "[Your Branch]"

    skills_section_match = re.search(r"(?:Skills|Technical Skills|Key Skills|Expertise)[:\n](.*?)(?=\n\n|Experience|Projects|Education|$)", resume_text, re.DOTALL | re.IGNORECASE)
    found_skills = skills_section_match.group(1).strip().split(', ') if skills_section_match else []
    found_skills = [skill.strip() for skill in found_skills if skill.strip()]

    project_match = re.findall(r"(?:Project:|Worked on|Research on) ([\w\s]+)", resume_text)
    projects = ", ".join(set(project_match)) if project_match else "various projects"

    ollama_prompt = f"""
    Generate a professional self-introduction based on the following details:
    Name: {name}
    Branch: {branch}
    Skills: {', '.join(found_skills) if found_skills else 'Not Mentioned'}
    Projects: {projects}

    The introduction should be clear, professional, and engaging.
    """

    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": ollama_prompt}])
        generated_intro = response['message']['content'] if response else "Hello! I am a passionate learner looking to improve my skills."
    except Exception:
        generated_intro = "Hello! I am a passionate learner looking to improve my skills."

    return generated_intro

# Function to generate a common self-introduction
def generate_common_intro():
    ollama_prompt = "Generate a professional yet general self-introduction for a student aspiring in the tech field."
    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": ollama_prompt}])
        return response['message']['content'] if response else "Hello! I am an aspiring technology enthusiast eager to learn and grow in AI and ML."
    except Exception:
        return "Hello! I am an aspiring technology enthusiast eager to learn and grow in AI and ML."

# UI Components

st.markdown("<h1 style='text-align:center; font-size:30px;'>🤖 AI-Powered Self-Intro Practice:</h1>", unsafe_allow_html=True)


resume_file = st.file_uploader("📥 Upload Your Resume (PDF or DOCX)", type=["pdf", "docx"])

st.subheader("💬 Enter Your Introduction or Skills Here:")
text = st.text_area("Type or paste your details here...", height=200)

if st.button("Assess Feedback"):
    st.session_state.history = []

    resume_text = ""
    suggested_intro = ""

    if resume_file:
        if resume_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_file)
        else:
            resume_text = extract_text_from_docx(resume_file)
        
        suggested_intro = extract_resume_summary(resume_text)
    else:
        suggested_intro = generate_common_intro()

    st.session_state.history.append(
    {'text': suggested_intro, 'sentiment': "Suggested Self-Introduction ✨",
     'scaled_score': "-", 'suggestion': "Refine your skills section by showcasing relevant technologies and projects that align with the job role.💡", 'color': "lightblue"}
)


    if text.strip():
        sentiment_score = TextBlob(text).sentiment.polarity
        scaled_score = ((sentiment_score + 1) / 2) * 98  # Scale score from 0 to 98

        if len(text.split()) < 3:
            sentiment = "Strongly Negative ❌"
            color = "red"
            scaled_score = 5
            suggestion = "Try writing a more complete introduction."

        elif scaled_score <= 10:
            sentiment = "Strongly Negative ❌"
            color = "red"
            suggestion = "Consider focusing on improvement and confidence-building."

        elif scaled_score <= 40:
            sentiment = "Negative ❗"
            color = "lightcoral"
            suggestion = "It might help to highlight strengths more clearly."

        elif scaled_score <= 60:
            sentiment = "Neutral 😐"
            color = "lightsteelblue"
            suggestion = "Try adding more details or enthusiasm to your introduction."

        elif scaled_score <= 80:
            sentiment = "Positive ✅"
            color = "lightgreen"
            suggestion = "Great! Keep nurturing your passion."

        else:
            sentiment = "Strongly Positive 🎉"
            color = "green"
            suggestion = "Keep up the positive attitude and keep growing!"

        st.session_state.history.append({'text': text, 'sentiment': sentiment, 'scaled_score': round(scaled_score, 2), 'suggestion': suggestion, 'color': color})
    else:
        st.warning("⚠️ Please enter some text before analyzing.")

# Display results
for entry in st.session_state.history:
    st.markdown(f"<h3 style='color:{entry['color']};'>{entry['sentiment']}</h3>", unsafe_allow_html=True)
    st.write(f"**Text Entered:** {entry['text']}")
    st.write(f"**Confidence Score:** {entry['scaled_score']}%")
    st.write(f"**Suggestion:** {entry['suggestion']}")
    st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h2 style='font-size:30px; color:white;'>🔍 Access Additional Help Here</h2>", unsafe_allow_html=True)

# Expander for "How to say a proper intro?"
with st.expander("How to say a proper intro?"):
    st.write("A proper intro should include who you are, what you do, and your goals. Here's a sample:")
    st.markdown("<p style='font-size:18px; color:white;'>"
                "'Hello! My name is [Your Name], and I am deeply passionate about [Your Field], particularly in the areas of [specific interest within the field]. Currently, I am honing my skills in [Skills/Technologies], and I am excited to apply my knowledge in [specific applications or industries]. My ultimate goal is to contribute to [specific goal or impact], and I am eager to continue growing and collaborating with like-minded professionals.'</p>", unsafe_allow_html=True)

# Expander for "What skills should you build?"
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

# Expander for "Suggested Videos for Career Growth and Motivation"
with st.expander("Suggested Videos for Career Growth and Motivation"):
    st.write("Check out these videos to inspire your career journey and decision-making:")
    
    st.markdown(""" 
    - **[How to Choose the Right Career Path | Best Advice](https://youtu.be/h-NjW4Wupzs?si=efERJ69321495G1S)**
    - **[The Psychology of Success | Stay Motivated and Focused](https://youtu.be/8ZhoeSaPF-k?si=Dq2ep-e4T43tQ2C5)**
    - **[Time Management & Productivity Hacks for Students](https://youtu.be/JmOBM160jZ0?si=lNUBI5xk0I99U9rw)**
    """)

    st.write("Want to explore more videos?")
    st.markdown("[Search for more on YouTube](https://www.youtube.com/results?search_query=career+motivation+success+tips)  \n[Google Chrome Search](https://www.google.com/)")