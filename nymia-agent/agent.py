import os
import json
import streamlit as st
from google import genai
from google.genai import types

#Load key from file
if os.path.exists("api.txt"):
    with open("api.txt", "r", encoding="utf-8") as f:
        os.environ["GEMINI_API_KEY"] = f.read().strip()

#Connect Gemini
client = genai.Client()

#---TOOLS---
def check_room_status() -> str:
    """Check room availability."""
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    available_rooms = [r for r in data["rooms"] if r["status"] == "available"]
    
    if not available_rooms:
        return "All rooms are occupied."
        
    room_list = ", ".join([f"Room {r['id']} ({r['type']})" for r in available_rooms])
    return f"Available rooms: {room_list}."

def check_revenue(pin_code: str) -> str:
    """Check revenue (Requires PIN)."""
    #Security check
    if pin_code != "1234":
        return "Wrong PIN. Access denied."
    
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return f"Today revenue: {data['total_revenue_today']} VND."

#Tool list
nymia_tools = [check_room_status, check_revenue]

#---UI WORKFLOW---

st.title("NYMIA PMS - AI Assistant")
st.caption("Kaggle AI Agents Capstone Project")

#Init chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#Render old messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#Handle user input
if user_query := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        #Config agent
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an assistant for NYMIA RETREAT. "
                    "Help management check room status and revenue using tools. "
                    "Reply shortly in English. "
                    "If user asks about revenue, you must ask for PIN first. Then pass PIN to check_revenue tool."
                ),
                tools=nymia_tools,
                temperature=0.2
            )
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})