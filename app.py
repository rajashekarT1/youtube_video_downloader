import streamlit as st
import os
import requests
import yt_dlp
from io import BytesIO
from PIL import Image
import re
import glob
import shutil
import base64

# -------------------- YouTube Functions --------------------

def download_youtube_video(url, quality):
    try:
        video_id = extract_video_id(url)
        if not video_id:
            st.error("Invalid YouTube URL. Please provide a valid URL.")
            return False  # Indicate failure

        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)

        quality_map = {
            "high": "bestvideo+bestaudio",
            "medium": "bv*[height<=720]+ba",
            "low": "bv*[height<=480]+ba"
        }
        selected_format = quality_map.get(quality, "medium")

        ydl_opts = {
            'format': 'bestvideo*+bestaudio/best',  # Tries to merge but falls back to a single best format
            'outtmpl': os.path.join(output_dir, "%(title)s.%(ext)s"),
            'merge_output_format': 'mp4',  # Remove this line if still failing
            'postprocessors': [],  # Remove FFmpeg postprocessing
        }


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Unknown Title')

        # Fix special characters in filenames
        original_filename = max(glob.glob("downloads/*.mp4"), key=os.path.getctime)
        safe_filename = re.sub(r'[\\/*?:"<>|]', "", video_title).replace(" ", "_") + ".mp4"
        final_filename = os.path.join(output_dir, safe_filename)

        shutil.move(original_filename, final_filename)

        st.success(f"✅ Downloaded")
        st.video(final_filename)

        with open(final_filename, "rb") as file:
            st.markdown(
                """
                <style>
                .download-button {
                    color: white !important;  /* Text color for the button */
                    background-color: #F00000 !important;
                    border-color: #F00000 !important;
                    text-align: center; /* center the text */
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.download_button(
                label="⬇ Download Video",
                data=file,
                file_name=safe_filename,
                mime="video/mp4",
                use_container_width=True,
                key="download_button"
            )
        return True # Indicate success

    except yt_dlp.utils.DownloadError as e:
        st.error(f"❌ Download failed: {e}")
        return False  # Indicate failure
    except Exception as e:
        st.error(f"⚠ Unexpected error: {e}")
        return False # Indicate failure


# -------------------- Progress Hook --------------------

def clean_ansi(text):
    """Removes ANSI escape codes from progress output."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def progress_hook(d):
    pass


# -------------------- Main Functions --------------------

def extract_video_id(url):
    pattern = r"(?:v=|\/(?:vi|v|e|embed)\/|youtu\.be\/|watch\?v=)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def show_downloader():
    st.markdown("<h1 style='text-align: center;'>🎥 YouTube Downloader</h1>", unsafe_allow_html=True)

    quality_options = ["high", "medium", "low"]
    selected_quality = st.radio("Select Quality:", quality_options, horizontal=True)

    youtube_url = st.text_input("🔗 Enter YouTube Video URL:", placeholder="Paste the YouTube URL here")

    if st.button("📥 Download Video", type="primary"): # Added type="primary" for a blue button.
        if youtube_url:
            download_youtube_video(youtube_url, selected_quality)


def set_bg_image(image_path):
    """Sets the background image of the Streamlit app."""
    with open(image_path, "rb") as f:
        img_data = f.read()
    img = Image.open(BytesIO(img_data))
    width, height = img.size
    encoded_image = base64.b64encode(img_data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_image}");
            background-size: cover;
            background-repeat: no-repeat;
            min-height: {height}px;
            color: white;
        }}
        .stButton > button {{
            color: white !important; /* Text color */
            background-color: #F00000 !important; /* Red background */
            border-color: #F00000 !important;  /* Red border */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def main():
    set_bg_image("background.jpg")
    show_downloader()

if __name__ == '__main__':
    main()
