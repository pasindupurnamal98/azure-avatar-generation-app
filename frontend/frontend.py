import streamlit as st
import requests

st.set_page_config(page_title="Azure AI Avatar Generator", layout="centered")

st.title("🎙️ Azure AI Avatar Video Generator")

# --- Input Fields ---
script_text = st.text_area("📝 Enter your script", height=150, value="Hello! I'm Ava from Azure.")

voice = st.selectbox("🗣️ Select Voice", [
    "en-US-AvaMultilingualNeural", "en-US-JennyNeural", "en-US-DavisNeural"
])

avatar = st.selectbox("🧍 Select Avatar", [
    "Lisa", "Harry", "Lori", "Max", "Meg"
])

style = st.selectbox("🎭 Select Avatar Style", [
    "business", "casual", "youthful", "formal", 
    "casual-sitting", "graceful-sitting", "graceful-standing", 
    "technical-sitting", "technical-standing"
])

# --- Background Upload ---
st.subheader("🖼️ Optional: Upload Background Image")
uploaded_image = st.file_uploader("Upload a background image (JPG or PNG)", type=["jpg", "jpeg", "png"])

background_image_url = None

if uploaded_image:
    st.image(uploaded_image, caption="Preview of Uploaded Background", use_column_width=True)

    with st.spinner("Uploading image to backend..."):
        files = {"file": (uploaded_image.name, uploaded_image, uploaded_image.type)}
        upload_response = requests.post("http://localhost:8000/upload-background", files=files)

        if upload_response.status_code == 200:
            background_image_url = upload_response.json().get("url")
            st.success("✅ Image uploaded successfully!")
            st.info(f"Background Image URL: {background_image_url}")
        else:
            st.error("❌ Failed to upload image.")
            st.code(upload_response.text)

# --- Generate Button ---
if st.button("🎬 Generate Avatar Video"):
    if not script_text.strip():
        st.warning("⚠️ Please enter a script before generating the video.")
    else:
        with st.spinner("⏳ Generating video... please wait up to 2 minutes"):
            payload = {
                "script_text": script_text,
                "voice": voice,
                "avatar": avatar,
                "style": style
            }
            if background_image_url:
                payload["backgroundImage"] = background_image_url

            response = requests.post("http://localhost:8000/generate-avatar", json=payload)

            if response.status_code == 200:
                data = response.json()
                video_url = f"http://localhost:8000{data['download_url']}"
                st.success("✅ Video generated successfully!")
                st.video(video_url)
                st.markdown(f"[📥 Download Video]({video_url})", unsafe_allow_html=True)
            else:
                st.error("❌ Failed to generate avatar video.")
                st.code(response.text)
