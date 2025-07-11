import streamlit as st
import requests
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import time
from datetime import datetime

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🌤️ Weather Assistant",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with dark mode support
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    /* Dark mode support for main header */
    [data-theme="dark"] .main-header {
        color: #4FC3F7;
    }
    
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid;
        color: #1f2937;
    }
    
    /* Dark mode support for chat messages */
    [data-theme="dark"] .chat-message {
        color: #e5e7eb;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #2E86AB;
    }
    
    /* Dark mode for user messages */
    [data-theme="dark"] .user-message {
        background-color: #374151;
        border-left-color: #4FC3F7;
    }
    
    .assistant-message {
        background-color: #e8f4f8;
        border-left-color: #00d4aa;
    }
    
    /* Dark mode for assistant messages */
    [data-theme="dark"] .assistant-message {
        background-color: #1f2937;
        border-left-color: #34d399;
    }
    
    .tool-message {
        background-color: #fff3cd;
        border-left-color: #ffc107;
        font-size: 0.9em;
    }
    
    /* Dark mode for tool messages */
    [data-theme="dark"] .tool-message {
        background-color: #451a03;
        border-left-color: #f59e0b;
    }
    
    .sidebar-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #1f2937;
    }
    
    /* Dark mode for sidebar info */
    [data-theme="dark"] .sidebar-info {
        background-color: #374151;
        color: #e5e7eb;
    }
    
    /* Additional dark mode text fixes */
    [data-theme="dark"] .main-header p {
        color: #9ca3af;
    }
    
    /* Strong text in dark mode */
    [data-theme="dark"] .chat-message strong {
        color: #f9fafb;
    }
    
    /* Sidebar info strong text */
    [data-theme="dark"] .sidebar-info strong {
        color: #f3f4f6;
    }
    
    /* Footer text in dark mode */
    [data-theme="dark"] .footer-text {
        color: #9ca3af;
    }
    
    /* Auto-detect system theme */
    @media (prefers-color-scheme: dark) {
        .main-header {
            color: #4FC3F7;
        }
        
        .main-header p {
            color: #9ca3af;
        }
        
        .chat-message {
            color: #e5e7eb;
        }
        
        .user-message {
            background-color: #374151;
            border-left-color: #4FC3F7;
        }
        
        .assistant-message {
            background-color: #1f2937;
            border-left-color: #34d399;
        }
        
        .tool-message {
            background-color: #451a03;
            border-left-color: #f59e0b;
        }
        
        .sidebar-info {
            background-color: #374151;
            color: #e5e7eb;
        }
        
        .chat-message strong {
            color: #f9fafb;
        }
        
        .sidebar-info strong {
            color: #f3f4f6;
        }
        
        .footer-text {
            color: #9ca3af;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Set up API key
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# ============================== Tool Creation ==============================

@tool
def get_weather(city: str):
    """
    Gets the current temperature for a given location.
    
    Args:
        city (str): The city name, e.g. Delhi
    """
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return f"The weather in {city} is {response.text}."
        return f"Could not fetch weather data for {city}. Please try again."
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

# Initialize chat model
@st.cache_resource
def init_model():
    return init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# ============================== Streamlit UI ==============================

# Header
st.markdown("""
<div class="main-header">
    <h1>🌤️ Weather Assistant</h1>
    <p>Your AI-powered weather companion using LangChain & Gemini</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔧 Settings")
    
    # Model info
    st.markdown("""
    <div class="sidebar-info">
        <strong>🤖 Model:</strong> Gemini 2.0 Flash<br>
        <strong>🛠️ Framework:</strong> LangChain<br>
        <strong>🌐 Weather API:</strong> wttr.in
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    popular_cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"]
    
    for city in popular_cities:
        if st.button(f"🌡️ {city}", key=f"quick_{city}"):
            st.session_state.quick_query = f"What's the weather in {city}?"
    
    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
    
    # Stats
    st.markdown("### 📊 Session Stats")
    st.metric("Messages", len(st.session_state.messages))
    st.metric("Weather Queries", len([m for m in st.session_state.messages if "weather" in m.get("content", "").lower()]))

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 Chat with Weather Assistant")
    
    # Chat input
    query = st.chat_input("Ask about weather in any city...")
    
    # Handle quick query from sidebar
    if 'quick_query' in st.session_state:
        query = st.session_state.quick_query
        del st.session_state.quick_query
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            elif message["role"] == "assistant":
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            elif message["role"] == "tool":
                st.markdown(f"""
                <div class="chat-message tool-message">
                    <strong>🔧 Tool:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)

with col2:
    st.markdown("### 🌈 Weather Info")
    
    # Weather status card
    current_time = datetime.now().strftime("%H:%M")
    st.markdown(f"""
    <div class="weather-card">
        <h3>🕒 Current Time</h3>
        <h2>{current_time}</h2>
        <p>Ready to help with weather queries!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    st.markdown("### 📝 How to Use")
    st.markdown("""
    1. **Type your query** in the chat input
    2. **Ask about weather** in any city
    3. **Use quick buttons** in the sidebar
    4. **Get real-time weather** information
    
    **Example queries:**
    - "What's the weather in Delhi?"
    - "How's the temperature in Mumbai?"
    - "Tell me about weather in London"
    """)

# Process user input
if query:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Show processing indicator
    with st.spinner("🤖 Processing your request..."):
        try:
            # Initialize model
            llm = init_model()
            tools = [get_weather]
            llm_with_tools = llm.bind_tools(tools)
            
            # Create message chain
            messages = [HumanMessage(query)]
            ai_msg = llm_with_tools.invoke(messages)
            
            # Handle tool calls
            if ai_msg.tool_calls:
                # Add AI message with tool calls
                messages.append(ai_msg)
                
                # Execute tools
                for tool_call in ai_msg.tool_calls:
                    if tool_call["name"].lower() == "get_weather":
                        tool_result = get_weather.invoke(tool_call["args"])
                        # Add tool message to chat history
                        st.session_state.messages.append({
                            "role": "tool", 
                            "content": f"🌡️ Weather data fetched: {tool_result}"
                        })
                        messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
                
                # Get final response
                final_answer = llm_with_tools.invoke(messages)
                response_content = final_answer.content
            else:
                response_content = ai_msg.content
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response_content})
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Rerun to show updated messages
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div class="footer-text" style="text-align: center; color: #666; padding: 1rem;">
    Built with ❤️ using Streamlit, LangChain & Google Gemini | 
    Weather data from <a href="https://wttr.in" target="_blank">wttr.in</a>
</div>
""", unsafe_allow_html=True)