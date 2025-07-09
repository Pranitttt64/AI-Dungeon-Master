import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import re

st.set_page_config(page_title="AI Dungeon Master", page_icon="🧙‍♂️")

#  MODEL LOADING 
@st.cache_resource
def load_model():
    model_name = "gpt2-medium"  # other models.... gpt2, distilgpt2
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()

#  STORY GENERATION 

def generate_story(prompt: str) -> str:
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(
        input_ids,
        max_length=len(input_ids[0]) + 100,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.8,
        top_k=40,
        top_p=0.9,
        repetition_penalty=1.2,
        num_return_sequences=1,
    )
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    return decoded.strip()

def clean_response(text: str) -> str:
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"[^\x00-\x7F]+", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

#  INITIAL STATE 

if "story" not in st.session_state:
    st.session_state.story = "You wake up in a dark enchanted forest. A dragon roars in the distance..."

if "pending_input" not in st.session_state:
    st.session_state.pending_input = None

#  UI

st.title("🧙‍♂️ AI Dungeon Master")
st.markdown("Write your moves and let the AI generate the next part of your fantasy adventure!")

#  Custom start
with st.expander("📝 Customize Start"):
    custom_start = st.text_input("Enter your custom opening line:")
    if st.button("🚀 Start New Adventure") and custom_start.strip():
        st.session_state.story = custom_start.strip()
        st.session_state.pending_input = None
        if "user_move" in st.session_state:
            del st.session_state["user_move"]
        st.rerun()

if st.button("🔄 Reset Story"):
    st.session_state.story = "You wake up in a dark enchanted forest. A dragon roars in the distance..."
    st.session_state.pending_input = None
    if "user_move" in st.session_state:
        del st.session_state["user_move"]
    st.rerun()

st.markdown("### 📖 Story So Far")
st.markdown(f"```\n{st.session_state.story}\n```")

# User Input
with st.form("input_form"):
    user_input = st.text_input("Your move:", key="user_move")
    submitted = st.form_submit_button("Submit")

# Handle input
if submitted and user_input:
    st.session_state.pending_input = user_input
    st.rerun()

#  RESPONSE HANDLING 

if st.session_state.pending_input:
    with st.spinner("Crafting your next move..."):

        last_lines = "\n".join(st.session_state.story.strip().split("\n")[-6:])
        prompt = (
            "You are an AI Dungeon Master. Continue the fantasy adventure story vividly.\n"
            + last_lines
            + f"\nYou: {st.session_state.pending_input}\nAI:"
        )

        raw_response = generate_story(prompt)
        cleaned = clean_response(raw_response)

        if "AI:" in cleaned:
            cleaned = cleaned.split("AI:")[-1].strip()

        cleaned = cleaned.replace(st.session_state.pending_input.strip(), "").strip()

        st.session_state.story += f"\nYou: {st.session_state.pending_input}\nAI: {cleaned}"

    # Clear input and rerun
    st.session_state.pending_input = None
    if "user_move" in st.session_state:
        del st.session_state["user_move"]
    st.rerun()
