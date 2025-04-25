import streamlit as st
import requests

# List of available Azure Neural Voices (customize as needed)
voice_options = {
    "Jenny (US English)": "en-US-JennyNeural",
    "Ryan (US English)": "en-US-RyanNeural",
    "Sonia (UK English)": "en-GB-SoniaNeural",
    "Aria (US English)": "en-US-AriaNeural",
    "Prabodh (Hindi India)": "hi-IN-PrabodhNeural"
}

# List of available avatars (use the ones supported in your Azure region)
avatar_options = {
    "Lisa": "lisa",
    "John": "john",
    "Emily": "emily",
    "Noah": "noah",
    "Maya": "maya"
}

st.title("🎥 Azure AI Avatar Generator")

script = st.text_area("📜 Enter your script:", height=150)

selected_voice_label = st.selectbox("🎤 Select Voice", list(voice_options.keys()))
selected_avatar_label = st.selectbox("🧑 Select Avatar", list(avatar_options.keys()))

selected_voice = voice_options[selected_voice_label]
selected_avatar = avatar_options[selected_avatar_label]

if st.button("🚀 Generate Avatar"):
    payload = {
        "script_text": script,
        "voice": selected_voice,
        "avatar": selected_avatar
    }
    response = requests.post("http://localhost:8000/generate-avatar", json=payload)
    
    if response.status_code == 200:
        download_url = response.json()["download_url"]
        st.video(f"http://localhost:8000{download_url}")
        st.markdown(f"[📥 Click here to download your video](http://localhost:8000{download_url})", unsafe_allow_html=True)
    else:
        st.error("❌ Avatar generation failed")
