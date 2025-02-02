import streamlit as st
from textblob import TextBlob
from PIL import Image

st.set_page_config(page_title="Sentiment Analyzer", page_icon="🎭", layout="centered")

page_bg_img = '''
<style>

.stButton>button {
    display: block;
    margin: 0 auto;
    border: 2px solid white;  
    border-radius: 10px;
    background-color: transparent;
    padding: 10px 20px;
    color: white;
    font-size: 16px;
    box-shadow: 0 0 6px 1px white; 
    transition: box-shadow 0.3s ease-in-out, border-color 0.3s ease-in-out; 
}

.stButton>button:hover {
    box-shadow: 0 0 10px 3px white; 
    border-color: skyblue; 
}


.stTextArea textarea {
    border: 2px solid white;  
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 0 6px 1px white; 
    transition: box-shadow 0.3s ease-in-out; 
    background-color: transparent;
    color: white;  
}

.stTextArea textarea:focus {
    border-color: skyblue;  
    box-shadow: 0 0 10px 3px skyblue;  
    color: white;  
}


.stTextArea textarea:hover {
    border-color: skyblue; 
    box-shadow: 0 0 10px 3px skyblue; 
    color: white;  
}

.stTextInput input {
    border: 2px solid white;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 0 6px 1px white; 
    transition: box-shadow 0.3s ease-in-out; 
    background-color: transparent;
    color: white;  
}

.stTextInput input:focus {
    border-color: skyblue;  
    box-shadow: 0 0 10px 3px skyblue;  
    color: white;  
}
.stTextInput input:hover {
    border-color: skyblue; 
    box-shadow: 0 0 10px 3px skyblue; 
    color: white;  
}


.stExpander {
    border: 2px solid white; 
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 0 3px 1px white; 
    transition: box-shadow 0.3s ease-in-out; 
    color: white; 
}

.stExpander:hover,
.stExpander:focus-within {
    box-shadow: 0 0 4px 2px white; 
    color: skyblue;  
}

.stExpander .stMarkdown,
.stExpander .stWrite {
    color: white; 
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🔍 Sentiment Analysis App</h1>", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

st.subheader("Enter your self-introduction or skills:")
text = st.text_area("Type or paste your details here...", height=200)

if st.button("Assess Feedback"):
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
            color = "gray"
            suggestion = "Try adding more details or enthusiasm to your introduction."

        st.session_state.history.append({
            'text': text,
            'sentiment': sentiment,
            'scaled_score': round(scaled_score, 2),
            'suggestion': suggestion,
            'color': color
        })
        
    else:
        st.warning("⚠️ Please enter some text before analyzing.")

for entry in st.session_state.history:
    st.markdown(f"<h3 style='color:{entry['color']};'>{entry['sentiment']}</h3>", unsafe_allow_html=True)
    st.write(f"**Text Entered:** {entry['text']}")
    st.write(f"**Confidence Score:** `{entry['scaled_score']}%`")
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
    st.write("- **For Web Development**: HTML, CSS, JavaScript, React, Node.js")
    st.write("- **For Mobile Development**: Java, Swift, Android Studio, Flutter")
    st.write("- **For Soft Skills**: Communication, Teamwork, Problem-Solving, Critical Thinking")
    st.write("Search for more specific skills related to your interests and role!")

with st.expander("Suggested Videos for Self-Introduction and Career Roadmap"):
    st.write("Check out these videos to improve your introduction and career planning:")
    
    st.markdown(""" 
    - **[How to Craft the Perfect Self-Introduction | Personal Branding](https://youtu.be/ozMCb0wOnMU?si=k0PfsWeQ_hoq7mfQ)**
    - **[AI & ML Career Roadmap | Path to becoming an AI Engineer](https://www.youtube.com/watch?v=J_YLjCTOFWE&pp=ygU4QUkgJiBNTCBDYXJlZXIgUm9hZG1hcCB8IFBhdGggdG8gYmVjb21pbmcgYW4gQUkgRW5naW5lZXI%3D)**
    - **[Top Skills to Build for a Career in Tech | Key Skills for 2025](https://www.youtube.com/watch?v=zUFb9UAKgjw&pp=ygVSXVRvcCBTa2lsbHMgdG8gQnVpbGQgZm9yIGEgQ2FyZWVyIGluIFRlY2ggfCBLZXkgU2tpbGxzIGZvciAyMDI1IGJ5IGNvZGUgd2l0aCBoYXJyeQ%3D%3D)**
    """)
    
    st.write("Want to explore more videos?")
    st.markdown("[Search for more on YouTube](https://www.youtube.com/results?search_query=career+roadmap+AI+ML+introduction+skills+development)")
