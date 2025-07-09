import streamlit as st
import os
import re
from openai import OpenAI
from openai.types import Completion
from openai.types.chat import ChatCompletionMessage

# Load OpenAI API key
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))

st.set_page_config(page_title="AI Dungeon Master", page_icon="🧙‍♂️")
st.title("🧙‍♂️ AI Dungeon Master")
st.markdown("Enter your moves, and let the AI Dungeon Master create the adventure!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are an AI Dungeon Master guiding a fantasy text adventure. Be vivid, logical, and stay in-character."},
        {"role": "user", "content": "Start the story."},
        {"role": "assistant", "content": "You wake up in a dark enchanted forest. A dragon roars in the distance..."}
    ]

story_text = "\n".join(
    f"You: {msg['content']}" if msg["role"] == "user" else f"AI: {msg['content']}"
    for msg in st.session_state.chat_history[2:]
)
st.markdown("### 📖 Story So Far")
st.text_area("Story", value=story_text.strip(), height=400, disabled=True)

if st.button("🔄 Reset Story"):
    st.session_state.chat_history = [
        {"role": "system", "content": "You are an AI Dungeon Master guiding a fantasy text adventure. Be vivid, logical, and stay in-character."},
        {"role": "user", "content": "Start the story."},
        {"role": "assistant", "content": "You wake up in a dark enchanted forest. A dragon roars in the distance..."}
    ]
    st.rerun()

# Input form
with st.form("input_form"):
    user_input = st.text_input("Your move:")
    submitted = st.form_submit_button("Submit")

if submitted and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("The Dungeon Master is crafting your story..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.chat_history,
                temperature=0.9,
                max_tokens=200,
                top_p=0.95,
                frequency_penalty=0.3,
                presence_penalty=0.6
            )

            reply = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
