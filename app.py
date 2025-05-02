import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state for feedback
if 'feedback_history' not in st.session_state:
    st.session_state.feedback_history = {}

# Initialize session state for chat input
if 'chat_input' not in st.session_state:
    st.session_state.chat_input = ""

# Initialize session state for profile visibility
if 'show_profile' not in st.session_state:
    st.session_state.show_profile = False

# Custom CSS
st.markdown("""
    <style>
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.1);
    }
    
    .chat-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    /* User message styling */
    .user-message {
        background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
        margin-left: 20%;
        border-left: 4px solid #90e0ef;
        color: white;
    }
    
    /* Bot message styling */
    .bot-message {
        background: linear-gradient(135deg, #2a2a72 0%, #009ffd 100%);
        margin-right: 20%;
        border-right: 4px solid #90e0ef;
        color: white;
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 25px;
        padding: 12px 20px;
        border: 2px solid #90e0ef;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #00b4d8;
        box-shadow: 0 0 10px rgba(0,180,216,0.5);
        background: rgba(255, 255, 255, 0.15);
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 25px;
        padding: 12px 30px;
        background: linear-gradient(45deg, #00b4d8, #0077b6);
        color: white;
        border: none;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,180,216,0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(144, 224, 239, 0.2);
    }
    
    .css-1d391kg::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #00b4d8, #0077b6);
    }
    
    /* Sidebar elements */
    .sidebar .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(144, 224, 239, 0.3);
        border-radius: 20px;
        padding: 12px 15px;
        color: white;
        font-size: 14px;
    }
    
    .sidebar .stTextInput>div>div>input::placeholder {
        color: rgba(255, 255, 255, 0.6);
    }
    
    .sidebar .stSelectbox>div>div>div {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(144, 224, 239, 0.3);
        border-radius: 20px;
        color: white;
    }
    
    .sidebar .stMultiSelect>div>div>div {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(144, 224, 239, 0.3);
        border-radius: 20px;
        color: white;
    }
    
    /* Sidebar headers */
    .sidebar h2 {
        color: #90e0ef;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(144, 224, 239, 0.3);
    }
    
    /* Sidebar labels */
    .sidebar label {
        color: #90e0ef;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    /* Title styling */
    h1 {
        color: #90e0ef;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Header styling */
    h2 {
        color: #90e0ef;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    /* Feedback buttons */
    .feedback-button {
        padding: 10px 20px;
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    
    .like-button:hover {
        background: linear-gradient(45deg, #4caf50, #2e7d32);
        color: white;
    }
    
    .dislike-button:hover {
        background: linear-gradient(45deg, #f44336, #c62828);
        color: white;
    }
    
    /* Add a subtle animation to the background */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp {
        background-size: 200% 200%;
        animation: gradientBG 15s ease infinite;
    }
    
    /* Profile section styling */
    .profile-section {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        border: 1px solid rgba(144, 224, 239, 0.3);
    }
    
    .profile-info {
        color: #90e0ef;
        margin-bottom: 10px;
    }
    
    .profile-label {
        font-weight: bold;
        color: #00b4d8;
    }
    </style>
    """, unsafe_allow_html=True)

def get_gemini_response(prompt):
    """Get optimized response from Gemini API"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    # Configure generation parameters for more comprehensive responses
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 500,  # Increased token limit for more detailed responses
    }
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )
    return response.text

def format_chat_message(role, content):
    """Format chat message for display with custom styling"""
    if role == "You":
        return f'<div class="chat-message user-message"><strong>{role}:</strong> {content}</div>'
    else:
        return f'<div class="chat-message bot-message"><strong>{role}:</strong> {content}</div>'

def main():
    st.title("Travel Souvenir Recommendation Chatbot")
    st.write("Get personalized souvenir recommendations for your next trip!")

    # Sidebar for user preferences with enhanced styling
    with st.sidebar:
        st.markdown('<div class="sidebar">', unsafe_allow_html=True)
        st.header("Travel Preferences")
        
        # Profile button
        if st.button("👤 Profile", key="profile_button"):
            st.session_state.show_profile = not st.session_state.show_profile
        
        # Profile section
        if st.session_state.show_profile:
            st.markdown('<div class="profile-section">', unsafe_allow_html=True)
            st.markdown('<h3>Profile Information</h3>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-info"><span class="profile-label">Name:</span> Avneet Kumar</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-info"><span class="profile-label">Email:</span> avneetchaudharycool9199@gmail.com</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-info"><span class="profile-label">Phone:</span> 9507995686</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<label>Where are you traveling to?</label>', unsafe_allow_html=True)
        destination = st.text_input("", key="destination", placeholder="Enter your destination")
        
        st.markdown('<label>Budget Range</label>', unsafe_allow_html=True)
        budget = st.selectbox("", ["Low", "Medium", "High"], key="budget")
        
        st.markdown('<label>What are you interested in?</label>', unsafe_allow_html=True)
        interests = st.multiselect(
            "",
            ["Art & Culture", "Food & Drinks", "Fashion", "Local Crafts", "Technology", "Nature", "History", "Adventure", "Shopping", "Beach", "Mountains", "Urban"],
            key="interests"
        )
        
        st.markdown('<label>Travel Duration</label>', unsafe_allow_html=True)
        duration = st.selectbox("", ["Short Trip (1-3 days)", "Medium Trip (4-7 days)", "Long Trip (8+ days)"], key="duration")
        
        st.markdown('<label>Travel Season</label>', unsafe_allow_html=True)
        season = st.selectbox("", ["Spring", "Summer", "Autumn", "Winter"], key="season")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Main chat interface
    st.header("Chat with the Bot")
    
    # Display chat history with custom styling
    for message in st.session_state.chat_history:
        st.markdown(message, unsafe_allow_html=True)

    # Create a form for chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask about souvenirs for your trip:", key="chat_input")
        submit_button = st.form_submit_button("Send")

    # Handle form submission outside the form context
    if submit_button and user_input:
        # Add user message to chat history
        st.session_state.chat_history.append(format_chat_message("You", user_input))
        
        # Create comprehensive context-aware prompt
        context = f"""
        Provide detailed and diverse recommendations for souvenirs based on the following travel details.
        Include multiple options (5-7 recommendations) that match the user's preferences.
        
        Travel Details:
        - Destination: {destination}
        - Budget: {budget}
        - Interests: {', '.join(interests)}
        - Duration: {duration}
        - Season: {season}
        
        User Question: {user_input}
        
        Guidelines for response:
        1. Provide 5-7 diverse souvenir recommendations
        2. For each recommendation:
           - Name and description of the item
           - Typical price range
           - Best places to buy it
           - Why it's special/unique to the destination
           - How it relates to the user's interests
        3. Include both traditional and modern options
        4. Consider the travel duration and season
        5. Provide budget-specific recommendations
        6. Include tips for authentic shopping
        7. Mention any seasonal specialties
        """
        
        # Get response from Gemini
        response = get_gemini_response(context)
        
        # Add bot response to chat history
        st.session_state.chat_history.append(format_chat_message("Bot", response))
        
        # Rerun to update chat display
        st.rerun()

    # Feedback section with custom styling
    if st.session_state.chat_history:
        st.header("Feedback")
        last_bot_message = st.session_state.chat_history[-1]
        if "Bot:" in last_bot_message:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Like", key="like_button", help="Click if you found this helpful"):
                    st.session_state.feedback_history[len(st.session_state.chat_history) - 1] = "like"
                    st.success("Thank you for your feedback!")
            with col2:
                if st.button("👎 Dislike", key="dislike_button", help="Click if this wasn't helpful"):
                    st.session_state.feedback_history[len(st.session_state.chat_history) - 1] = "dislike"
                    st.error("Thank you for your feedback!")

if __name__ == "__main__":
    main() 