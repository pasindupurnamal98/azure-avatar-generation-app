import streamlit as st
import requests

st.set_page_config(page_title="Azure AI Avatar Generator", layout="centered")

st.title("🎙️ Azure AI Avatar Video Generator")

script_text = st.text_area("📝 Enter your script", height=150, value="Hello! I'm Ava from Azure.")

voice = st.selectbox("🗣️ Select Voice", [
    "en-US-AvaMultilingualNeural", "en-US-JennyNeural", "en-US-DavisNeural"
])

avatar = st.selectbox("🧍 Select Avatar", [
    "Lisa", "Harry", "Lori", "Max","Meg"
])

style = st.selectbox("🧍 Select Avatar Style", [
    "business", "casual", "youthful", "formal","casual-sitting","graceful-sitting", "graceful-standing", "technical-sitting", "technical-standing"
    
])

if st.button("Generate Avatar Video"):
    with st.spinner("⏳ Generating video... please wait up to 2 minutes"):
        response = requests.post(
            "http://localhost:8000/generate-avatar",  # replace with deployed FastAPI URL if needed
            json={
                "script_text": script_text,
                "voice": voice,
                "avatar": avatar,
                "style": style
            }
        )

        if response.status_code == 200:
            data = response.json()
            video_url = f"http://localhost:8000{data['download_url']}"
            st.success("✅ Video generated successfully!")
            st.video(video_url)
            st.markdown(f"[📥 Download Video]({video_url})", unsafe_allow_html=True)
        else:
            st.error("❌ Failed to generate avatar video.")
            st.text(response.text)

# import streamlit as st
# import requests

# st.set_page_config(page_title="Azure AI Avatar Generator", layout="centered")
# st.title("🎙️ Azure AI Avatar Video Generator")

# # Script input
# script_text = st.text_area("📝 Enter your script", height=150, value="Hello! I'm Ava from Azure.")

# # Dropdowns
# voice = st.selectbox("🗣️ Select Voice", [
#     "en-US-AvaMultilingualNeural", "en-US-JennyNeural", "en-US-DavisNeural"
# ])

# avatar = st.selectbox("🧍 Select Avatar", [
#     "Lisa", "Harry", "Lori", "Max", "Meg"
# ])

# style = st.selectbox("🎭 Select Avatar Style", [
#     "business", "casual", "youthful", "formal",
#     "casual-sitting", "graceful-sitting", "graceful-standing",
#     "technical-sitting", "technical-standing"
# ])

# background_option = st.radio("🖼️ Background Type", ["White", "Black", "Transparent", "Custom Image"])

# background_color_map = {
#     "White": "#FFFFFFFF",
#     "Black": "#000000FF",
#     "Transparent": "transparent"
# }

# background_image_url = None

# if background_option == "Custom Image":
#     uploaded_file = st.file_uploader("📁 Upload Background Image", type=["png", "jpg", "jpeg"])
#     if uploaded_file:
#         with st.spinner("⏫ Uploading image..."):
#             files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
#             upload_res = requests.post("http://localhost:8000/upload-background", files=files)
#             if upload_res.status_code == 200:
#                 background_image_url = upload_res.json()["background_url"]
#                 st.success("✅ Image uploaded successfully!")
#                 # st.image(background_image_url, caption="Uploaded Background", use_column_width=True)
#                 st.image(background_image_url, caption="Uploaded Background", use_container_width=True)

#             else:
#                 st.error("❌ Failed to upload image.")
#                 st.text(upload_res.text)

# if st.button("🎬 Generate Avatar Video"):
#     with st.spinner("⏳ Generating video... please wait up to 2 minutes"):
#         background = background_color_map.get(background_option, "#FFFFFFFF")
#         payload = {
#             "script_text": script_text,
#             "voice": voice,
#             "avatar": avatar,
#             "style": style,
#             "background": background,
#             "backgroundImage": background_image_url
#         }

#         response = requests.post("http://localhost:8000/generate-avatar", json=payload)

#         if response.status_code == 200:
#             data = response.json()
#             video_url = f"http://localhost:8000{data['download_url']}"
#             st.success("✅ Video generated successfully!")
#             st.video(video_url)
#             st.markdown(f"[📥 Download Video]({video_url})", unsafe_allow_html=True)
#         else:
#             st.error("❌ Failed to generate avatar video.")
#             st.text(response.text)
