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
    # Updated regex to handle a broader range of YouTube URLs
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
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







# import streamlit as st
# import sqlite3
# import hashlib
# import os
# from pytube import YouTube
# import requests
# import base64
# from pytube.exceptions import RegexMatchError, VideoUnavailable, AgeRestrictedError, LiveStreamError, PytubeError, ExtractError
# from io import BytesIO
# from PIL import Image
# import re  # Import the regular expression module

# # -------------------- Database Functions --------------------

# DATABASE_NAME = "users.db"

# def create_table():
#     conn = sqlite3.connect(DATABASE_NAME)
#     c = conn.cursor()
#     c.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             username TEXT PRIMARY KEY,
#             password TEXT NOT NULL
#         )
#     """)
#     conn.commit()
#     conn.close()

# def add_user(username, password):
#     conn = sqlite3.connect(DATABASE_NAME)
#     c = conn.cursor()
#     hashed_password = hashlib.sha256(password.encode()).hexdigest()
#     try:
#         c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
#         conn.commit()
#         st.success("Account created successfully! Please log in.")
#     except sqlite3.IntegrityError:
#         st.error("Username already exists.  Please choose a different one.")
#     finally:
#         conn.close()

# def verify_user(username, password):
#     conn = sqlite3.connect(DATABASE_NAME)
#     c = conn.cursor()
#     c.execute("SELECT password FROM users WHERE username = ?", (username,))
#     result = c.fetchone()
#     conn.close()

#     if result:
#         hashed_password = result[0]
#         return hashlib.sha256(password.encode()).hexdigest() == hashed_password
#     else:
#         return False

# def user_exists(username):
#     conn = sqlite3.connect(DATABASE_NAME)
#     c = conn.cursor()
#     c.execute("SELECT username FROM users WHERE username = ?", (username,))
#     result = c.fetchone()
#     conn.close()
#     return result is not None

# def download_youtube_video(url, download_path=".", file_format="mp4"):
#     try:
#         video_id = extract_video_id(url)
#         if video_id:
#             url = f"https://www.youtube.com/watch?v={video_id}"
#         else:
#             st.error("Invalid YouTube URL. Please provide a valid URL or ID.")
#             return

#         yt = YouTube(url)

#         try:
#             video_title = yt.title  # This might fail
#         except Exception:
#             video_title = "Unknown Title"
#             st.warning("Could not fetch video title. Downloading anyway.")

#         st.info(f"Video title: {video_title}")

#         if file_format == "mp4":
#             stream = yt.streams.get_highest_resolution()
#             file_extension = ".mp4"
#         elif file_format == "mp3":
#             stream = yt.streams.filter(only_audio=True).first()
#             file_extension = ".mp3"
#         else:
#             st.error("Invalid file format selected.")
#             return

#         st.info(f"Downloading: {video_title}")

#         file_path = os.path.join(download_path, f"{video_title}{file_extension}")
#         stream.download(output_path=download_path, filename=f"{video_title}{file_extension}")

#         st.success(f"Downloaded: {video_title} to {download_path}")

#     except RegexMatchError:
#         st.error("Invalid YouTube URL.")
#     except VideoUnavailable:
#         st.error("Video is unavailable.")
#     except AgeRestrictedError:
#         st.error("Video is age restricted and cannot be downloaded.")
#     except LiveStreamError:
#         st.error("Cannot download live streams.")
#     except PytubeError as e:
#         st.error(f"Pytube error: {e}")
#     except ExtractError as e:
#         st.error(f"ExtractError: Could not extract video information. Error: {e}.")
#     except requests.exceptions.RequestException as e:
#         st.error(f"Network Error: {e}")
#     except Exception as e:
#         st.error(f"Download failed: {e}")


# def get_youtube_thumbnail(url):
#     try:
#         # Extract video ID from URL if a shortened URL is provided
#         video_id = extract_video_id(url)
#         if video_id:
#             url = f"https://www.youtube.com/watch?v={video_id}"  # Construct the full URL
#         else:
#             st.error("Invalid YouTube URL. Please provide a valid URL or ID.")
#             return None

#         yt = YouTube(url)
#         thumbnail_url = yt.thumbnail_url
#         try:
#             response = requests.get(thumbnail_url, stream=True)
#             response.raise_for_status()  # Raise an exception for bad status codes
#         except requests.exceptions.RequestException as e:
#             st.error(f"Network Error: Could not download thumbnail. Please check your internet connection. Error: {e}")
#             return None

#         image = Image.open(BytesIO(response.content))
#         return image

#     except (RegexMatchError, VideoUnavailable, PytubeError, ExtractError) as e: # Handle ExtractError
#         st.error(f"Error getting thumbnail: {e}")
#         return None
#     except Exception as e:
#         st.error(f"An unexpected error occurred: {e}")
#         return None


# def extract_video_id(url):
#     """Extracts the video ID from a YouTube URL or ID."""
#     # Regular expression to match various YouTube URL formats
#     match = re.search(
#         r"(?:v=|\/?vi\/|youtu\.be\/)([^&\s]+)",
#         url
#     )
#     if match:
#         return match.group(1)
#     elif re.match(r"^[a-zA-Z0-9_-]{11}$", url): # Check if the input *is* a video ID
#         return url  # Return it directly if it's a valid ID
#     else:
#         return None

# # -------------------- UI Functions --------------------

# def get_base64(bin_file):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# def set_background(png_file):
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     image_path = os.path.join(script_dir, png_file)
#     bin_str = get_base64(image_path)
#     page_bg_img = '''
#     <style>
#     .stApp {
#       background-image: url("data:image/png;base64,%s");
#       background-size: cover;
#     }
#     </style>
#     ''' % bin_str
#     st.markdown(page_bg_img, unsafe_allow_html=True)


# def show_login_page():
#     st.markdown("<h1 style='text-align: center; color: white;'>Login</h1>", unsafe_allow_html=True)
#     username = st.text_input("Username", key="login_username",  placeholder="Enter your username",  )
#     password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")

#     col1, col2 = st.columns([1, 1])

#     with col1:
#         if st.button("Login", use_container_width=True):
#             if not username or not password:
#                 st.warning("Please enter both username and password.", icon="⚠️")
#             elif not user_exists(username):
#                 st.error("User does not exist. Please sign up.", icon="🚨")
#             elif verify_user(username, password):
#                 st.success(f"Logged in as {username}", icon="✅")
#                 st.session_state.logged_in = True
#                 st.session_state.username = username
#                 st.session_state.page = "downloader"
#                 st.rerun()
#             else:
#                 st.error("Incorrect Username/Password", icon="🚨")

#     with col2:
#         if st.button("Signup", use_container_width=True):
#             st.session_state.page = "signup"
#             st.rerun()

# def show_signup_page():
#     st.markdown("<h1 style='text-align: center; color: white;'>Create Account</h1>", unsafe_allow_html=True)
#     new_username = st.text_input("Username", key="signup_username", placeholder="Choose a username")
#     new_password = st.text_input("Password", type="password", key="signup_password", placeholder="Choose a strong password")

#     col1, col2 = st.columns([1, 1])

#     with col1:
#         if st.button("Signup", use_container_width=True):
#             if not new_username or not new_password:
#                 st.warning("Please enter both username and password.", icon="⚠️")
#             else:
#                 add_user(new_username, new_password)
#                 st.session_state.page = "login"
#                 st.rerun()

#     with col2:
#         if st.button("Login", use_container_width=True):
#             st.session_state.page = "login"
#             st.rerun()


# def show_downloader():
#     st.markdown("<h1 style='text-align: center; color: white;'>YouTube Downloader</h1>", unsafe_allow_html=True)
#     youtube_url = st.text_input("Enter YouTube URL or Video ID:", placeholder="Paste the YouTube URL or Video ID here")
#     download_path = os.getcwd()
#     # Remove the specific download path display
#     # st.info(f"Downloads will be saved to: {download_path}")

#     file_format = st.selectbox("Select file format:", ["mp4", "mp3"])

#     if youtube_url:
#         thumbnail = get_youtube_thumbnail(youtube_url)
#         if thumbnail:
#             st.image(thumbnail, caption="Video Thumbnail", use_column_width=True)

#     col1, col2, col3 = st.columns([1,1,1])

#     with col2:
#         if st.button("Download", use_container_width=True):
#             if youtube_url:
#                 download_youtube_video(youtube_url, download_path, file_format)
#             else:
#                 st.warning("Please enter a YouTube URL or Video ID.", icon="⚠️")

#     with col3:
#         if st.button("Logout", on_click=logout, use_container_width=True):
#             pass

# def logout():
#     st.session_state.logged_in = False
#     st.session_state.username = None
#     st.session_state.page = "login"
#     st.rerun()

# # -------------------- Main Function --------------------

# def main():

#     set_background('background.jpg')

#     st.markdown("""
#     <style>
#     body {
#         color: white;
#     }
#     .stTextInput > label {
#         color: white;
#     }
#     .stButton > button {
#         color: white;
#         background-color: #4CAF50;
#         border: none;
#         padding: 10px 20px;
#         text-align: center;
#         text-decoration: none;
#         display: inline-block;
#         font-size: 16px;
#         margin: 4px 2px;
#         cursor: pointer;
#         border-radius: 5px;
#     }
#     .stButton > button:hover {
#         background-color: #3e8e41;
#     }
#     </style>
#     """, unsafe_allow_html=True)


#     st.markdown("<h1 style='text-align: center; color: white;'>YouTube Downloader App</h1>", unsafe_allow_html=True)

#     create_table()

#     if 'logged_in' not in st.session_state:
#         st.session_state.logged_in = False
#     if 'username' not in st.session_state:
#         st.session_state.username = None
#     if 'page' not in st.session_state:
#         st.session_state.page = "login"

#     if st.session_state.logged_in:
#         show_downloader()
#     elif st.session_state.page == "login":
#         show_login_page()
#     elif st.session_state.page == "signup":
#         show_signup_page()


# if __name__ == '__main__':
#     main()






