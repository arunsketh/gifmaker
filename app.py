import streamlit as st
import tempfile
import os
import PIL.Image

# FIX: Restore ANTIALIAS for MoviePy compatibility with Pillow 10+
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import VideoFileClip

# Page Configuration
st.set_page_config(
    page_title="Secure AVI to GIF Converter",
    page_icon="🎬",
    layout="centered"
)

def check_password():
    """Returns `True` if the user had the correct password."""

    # --- SAFETY CHECK: Ensure the password is set in secrets ---
    if "password" not in st.secrets:
        # MODIFIED: For testing/preview, we warn instead of blocking if secrets are missing.
        st.warning("⚠️ 'password' key is missing in secrets. Running in INSECURE mode for testing.")
        st.info("To secure this app, create .streamlit/secrets.toml with: password = 'your_pass'")
        return True

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Enter Password to Access App", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input(
            "Enter Password to Access App", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    st.title("🎬 AVI to GIF Converter")
    st.write("Convert your AVI videos to GIF with custom settings.")

    # File Uploader
    uploaded_file = st.file_uploader("Upload an AVI file", type=["avi"])

    if uploaded_file is not None:
        # Save uploaded file to a temporary file
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".avi")
        tfile.write(uploaded_file.read())
        tfile.close()

        try:
            # Load video
            clip = VideoFileClip(tfile.name)
            duration = clip.duration
            original_width = clip.size[0]
            
            st.video(tfile.name)
            st.info(f"Original Duration: {duration:.2f} seconds | Resolution: {clip.size}")

            # --- Conversion Options ---
            st.divider()
            st.subheader("⚙️ Conversion Options")

            col1, col2 = st.columns(2)
            
            with col1:
                start_time = st.number_input("Start Time (seconds)", min_value=0.0, max_value=duration, value=0.0, step=0.5)
                # MODIFIED: Default value set to full duration
                end_time = st.number_input("End Time (seconds)", min_value=0.0, max_value=duration, value=duration, step=0.5)
            
            with col2:
                fps = st.slider("Frame Rate (FPS)", min_value=1, max_value=30, value=10, help="Lower FPS = smaller file size.")
                # MODIFIED: Default value set to original width, max value adjusts if video is larger than 1920
                max_slider_width = max(1920, original_width)
                width = st.slider("Resize Width (px)", min_value=100, max_value=max_slider_width, value=original_width, help="Smaller width significantly reduces file size.")

            # Logic check for time
            if start_time >= end_time:
                st.error("Error: End time must be greater than start time.")
            else:
                if st.button("Convert to GIF", type="primary"):
                    with st.spinner("Processing... This may take a moment."):
                        # Process clip
                        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".gif").name
                        
                        try:
                            # Subclip -> Resize -> Write
                            # We use .subclip() and .resize()
                            final_clip = clip.subclip(start_time, end_time).resize(width=width)
                            
                            final_clip.write_gif(output_path, fps=fps, verbose=False, logger=None)
                            
                            st.success("Conversion Complete!")
                            st.image(output_path, caption="Generated GIF Preview")
                            
                            # Derive new filename from uploaded file
                            original_name = uploaded_file.name
                            new_filename = os.path.splitext(original_name)[0] + ".gif"

                            # Download Button
                            with open(output_path, "rb") as file:
                                btn = st.download_button(
                                    label="Download GIF",
                                    data=file,
                                    file_name=new_filename,
                                    mime="image/gif"
                                )
                                
                        except Exception as e:
                            st.error(f"An error occurred during conversion: {e}")
                        finally:
                            # Cleanup GIF temp file
                            if os.path.exists(output_path):
                                os.remove(output_path)
                                
        except Exception as e:
            st.error(f"Error loading video file: {e}")
        finally:
            # Cleanup input temp file
            clip.close()
            os.remove(tfile.name)
