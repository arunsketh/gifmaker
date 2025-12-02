import streamlit as st
import tempfile
import os
from moviepy.editor import VideoFileClip

# --- Configuration ---
st.set_page_config(
    page_title="Network GIF Converter",
    page_icon="🎞️",
    layout="centered"
)

# --- Authentication Logic ---
def check_password():
    """Returns `True` if the user had the correct password."""

    # 1. Check if secrets are set up
    if "network_password" not in st.secrets:
        st.error("⚠️ Password not configured! Please create .streamlit/secrets.toml as per the README.")
        st.stop()
        
    correct_password = st.secrets["network_password"]

    def password_entered():
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input
        st.text_input(
            "Enter Network Access Key", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input again
        st.text_input(
            "Enter Network Access Key", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Access denied. Please ask the network admin for the key.")
        return False
    else:
        # Password correct
        return True

if check_password():
    # --- Main Application Logic ---
    st.title("🎞️ AVI to GIF Converter")
    st.markdown("Internal tool for converting video clips to optimized GIFs.")

    # 1. File Uploader
    uploaded_file = st.file_uploader("Upload a Video File (.avi, .mp4)", type=["avi", "mp4", "mov"])

    if uploaded_file is not None:
        # Save uploaded file to a temporary file so MoviePy can read it
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".avi")
        tfile.write(uploaded_file.read())
        
        # Open video with MoviePy
        try:
            clip = VideoFileClip(tfile.name)
        except Exception as e:
            st.error(f"Error loading video file. It might be corrupt. Details: {e}")
            st.stop()

        # --- Sidebar Settings ---
        st.sidebar.header("⚙️ Conversion Settings")
        
        speed = st.sidebar.slider("Playback Speed", 0.1, 4.0, 1.0, 0.1, help="Higher = Faster GIF")
        
        resize_factor = st.sidebar.select_slider(
            "Resolution Scaling",
            options=[0.3, 0.5, 0.75, 1.0],
            value=0.5,
            help="Reduce resolution to save file size."
        )
        
        fps_val = st.sidebar.slider("Frame Rate (FPS)", 5, 30, 10, help="Lower FPS = Smaller file size.")

        # --- Preview & Trimming ---
        st.subheader("1. Preview & Trim")
        
        if uploaded_file.name.lower().endswith(".avi"):
            st.warning("⚠️ Browser cannot play .AVI files directly. Use the slider below to preview frames.")
        
        duration = clip.duration
        start_time, end_time = st.slider(
            "Select Time Range (Seconds)",
            0.0, duration, (0.0, min(duration, 10.0)),
            step=0.1
        )
        
        preview_frame_time = st.slider("Preview Frame at (Seconds)", 0.0, duration, start_time)
        frame_at_time = clip.get_frame(preview_frame_time)
        st.image(frame_at_time, caption=f"Frame at {preview_frame_time}s", use_column_width=True)

        # --- Conversion ---
        st.subheader("2. Convert")
        
        if st.button("Generate GIF"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
            output_path = output_temp.name
            output_temp.close()

            try:
                status_text.text("Processing: Trimming & Resizing...")
                progress_bar.progress(20)
                
                final_clip = clip.subclip(start_time, end_time)
                final_clip = final_clip.resize(resize_factor)
                final_clip = final_clip.speedx(speed)
                
                status_text.text("Processing: Rendering GIF (This may take a moment)...")
                progress_bar.progress(50)
                
                final_clip.write_gif(output_path, fps=fps_val, verbose=False, logger=None)
                
                progress_bar.progress(100)
                status_text.success("Done!")

                st.subheader("3. Result")
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.image(output_path, caption="Generated GIF")
                
                with col2:
                    file_size = os.path.getsize(output_path) / (1024 * 1024)
                    st.metric(label="File Size", value=f"{file_size:.2f} MB")
                    
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="Download GIF",
                            data=f,
                            file_name="converted_animation.gif",
                            mime="image/gif"
                        )
            
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
            finally:
                pass

        clip.close()
        os.unlink(tfile.name)
