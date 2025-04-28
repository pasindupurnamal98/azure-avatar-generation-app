import os
import streamlit as st
import streamlit_authenticator as stauth
import requests

# --------------------------------------------------
# ----------- 0.  BASIC PAGE CONFIG  ---------------
# --------------------------------------------------
st.set_page_config(page_title="Azure AI Avatar Generator", layout="centered")
st.title("🎙️ Azure AI Avatar Video Generator")

# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Just the base URL, no path!
BACKEND_URL = os.getenv("BACKEND_URL", "http://azure-avtr-backend:8000")

# --------------------------------------------------
# ----------- 1.  AUTHENTICATION  ------------------
# --------------------------------------------------
# 📝 Demo credentials — replace or load from YAML/secrets in prod
names       = ["H One User"]
usernames   = ["demo"]
passwords   = ["demo123"]                         # plain text for demo ONLY
hashed_pwds = stauth.Hasher(passwords).generate() # -> ['$2b$12$Hash...']

credentials = {
    "usernames": {
        usernames[0]: {
            "name": names[0],
            "password": hashed_pwds[0]
        }
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="avatar_cookie",
    key="some_signature_key",
    cookie_expiry_days=7
)

name, auth_status, user = authenticator.login("🔐 Login", "sidebar")

if auth_status is False:
    st.error("Username / password is incorrect")
    st.stop()
elif auth_status is None:
    st.warning("Please log in to continue")
    st.stop()

# --------------------------------------------------
# ----------- 2.  MAIN APP UI  ---------------------
# --------------------------------------------------
st.success(f"👋 Welcome, {name}!")
authenticator.logout("Logout", "sidebar")
st.sidebar.markdown("---")

# --- Input Fields ---
script_text = st.text_area(
    "📝 Enter your script",
    height=150,
    value="Hello! I'm Lisa from Azure."
)

voice = st.selectbox("🗣️ Select Voice", [
    "en-US-AvaMultilingualNeural", "en-US-EmmaMultilingualNeural",
    "en-US-ChristopherMultilingualNeural", "en-US-JennyNeural",
    "en-US-AndrewMultilingualNeural", "en-US-DavisNeural"
])

avatar = st.selectbox("🧍 Select Avatar", [
    "Lisa", "Harry", "Lori", "Max", "Meg"
])

style = st.selectbox("🎭 Select Avatar Style", [
    "casual-sitting", "graceful", "business", "casual", "youthful", "formal",
    "graceful-standing", "technical-sitting", "technical-standing"
])

# --- Background Upload ---
st.subheader("🖼️ Optional: Upload Background Image")
uploaded_image = st.file_uploader(
    "Upload a background image (JPG/PNG)",
    type=["jpg", "jpeg", "png"]
)

background_image_url = None

if uploaded_image:
    st.image(uploaded_image, caption="Preview of Uploaded Background", use_column_width=True)

    with st.spinner("Uploading image…"):
        try:
            files = {"file": (uploaded_image.name, uploaded_image, uploaded_image.type)}
            resp  = requests.post(f"{BACKEND_URL}/upload-background", files=files, timeout=60)
            resp.raise_for_status()
        except requests.RequestException as e:
            st.error(f"❌ Failed to upload image: {e}")
        else:
            background_image_url = resp.json().get("url")
            st.success("✅ Image uploaded!")
            st.info(f"Background URL: {background_image_url}")

# --- Generate Button ---
if st.button("🎬 Generate Avatar Video"):
    if not script_text.strip():
        st.warning("⚠️ Please enter a script first.")
    else:
        with st.spinner("⏳ Generating video (may take ~2 min)…"):
            payload = {
                "script_text": script_text,
                "voice": voice,
                "avatar": avatar,
                "style": style
            }
            if background_image_url:
                payload["backgroundImage"] = background_image_url

            try:
                r = requests.post(f"{BACKEND_URL}/generate-avatar", json=payload, timeout=180)
                r.raise_for_status()
            except requests.RequestException as e:
                st.error(f"❌ Generation failed: {e}")
                st.stop()

            data = r.json()
            # video_url = f"{BACKEND_URL}{data['download_url']}"
            # st.success("✅ Video ready!")
            # st.video(video_url)
            # st.markdown(f"[📥 Download Video]({video_url})", unsafe_allow_html=True)
            video_url = f"{BACKEND_URL}{data['download_url']}"

            # Fetch the actual video bytes
            try:
                video_response = requests.get(video_url)
                video_response.raise_for_status()
            except requests.RequestException as e:
                st.error(f"❌ Failed to fetch video: {e}")
                st.stop()

            video_bytes = video_response.content

            st.success("✅ Video ready!")
            st.video(video_bytes)  # <-- now real video bytes
            st.download_button(
                label="📥 Download Video",
                data=video_bytes,
                file_name="avatar_video.mp4",
                mime="video/mp4"
            )


# --- Footer ---
st.markdown(
    "<hr style='margin-top:3rem;margin-bottom:1rem;'>"
    "<div style='text-align:center;font-size:0.85rem;color:gray;'>"
    "© H One Data and AI Team. All rights reserved."
    "</div>",
    unsafe_allow_html=True
)
