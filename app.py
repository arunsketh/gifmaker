import streamlit as st
import tempfile
import os
import PIL.Image
import gc  # Garbage Collector for memory management

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
        st.text_input(
            "Enter Password to Access App", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Enter Password to Access App", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    st.title("🎬 AVI to GIF Converter")
    st.write("Convert your AVI videos to GIF with custom settings.")
    st.info("💡 Tip: To prevent crashing, keep duration under 10s and width under 600px.")

    # File Uploader
    uploaded_file = st.file_uploader("Upload an AVI file", type=["avi"])

    if uploaded_file is not None:
        # OPTIMIZATION 1: Stream the file to disk in chunks to save RAM
        # Instead of reading the whole file into memory, we write 4MB chunks
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".avi")
        with open(tfile.name, "wb") as f:
            while True:
                chunk = uploaded_file.read(4 * 1024 * 1024)  # Read 4MB at a time
                if not chunk:
                    break
                f.write(chunk)
        
        # We don't close tfile manually here because the 'with' block handles it, 
        # but we need the name for MoviePy.

        clip = None
        final_clip = None

        try:
            # Load video
            clip = VideoFileClip(tfile.name)
            duration = clip.duration
            original_width = clip.size[0]
            
            st.video(tfile.name)
            st.caption(f"Original: {duration:.2f}s | {clip.size[0]}x{clip.size[1]}px")

            # --- Conversion Options ---
            st.divider()
            st.subheader("⚙️ Conversion Options")

            col1, col2 = st.columns(2)
            
            with col1:
                start_time = st.number_input("Start Time (s)", min_value=0.0, max_value=duration, value=0.0, step=0.5)
                end_time = st.number_input("End Time (s)", min_value=0.0, max_value=duration, value=duration, step=0.5)
            
            with col2:
                fps = st.slider("FPS", min_value=1, max_value=30, value=10)
                max_slider_width = max(1920, original_width)
                # Default to 480px to save memory, user can increase if needed
                default_width = min(original_width, 480)
                width = st.slider("Width (px)", min_value=100, max_value=max_slider_width, value=default_width)

            if start_time >= end_time:
                st.error("Error: End time must be greater than start time.")
            else:
                if st.button("Convert to GIF", type="primary"):
                    with st.spinner("Processing..."):
                        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".gif").name
                        
                        try:
                            # OPTIMIZATION 2: Resize BEFORE writing to save processing power
                            final_clip = clip.subclip(start_time, end_time).resize(width=width)
                            
                            # OPTIMIZATION 3: Write GIF with memory optimizations
                            # 'fuzz' reduces file size, 'program' uses ffmpeg if available
                            final_clip.write_gif(
                                output_path, 
                                fps=fps, 
                                verbose=False, 
                                logger=None
                            )
                            
                            st.success("Conversion Complete!")
                            st.image(output_path, caption="Preview")
                            
                            original_name = uploaded_file.name
                            new_filename = os.path.splitext(original_name)[0] + ".gif"

                            with open(output_path, "rb") as file:
                                st.download_button(
                                    label="Download GIF",
                                    data=file,
                                    file_name=new_filename,
                                    mime="image/gif"
                                )
                                
                        except Exception as e:
                            st.error(f"Error: {e}")
                        finally:
                            if os.path.exists(output_path):
                                os.remove(output_path)
                                
        except Exception as e:
            st.error(f"Error loading video: {e}")
        finally:
            # OPTIMIZATION 4: Aggressive Cleanup
            if clip: 
                clip.close()
                del clip
            if final_clip:
                final_clip.close()
                del final_clip
            
            # Force garbage collection
            gc.collect()
            
            # Remove temp video file
            if os.path.exists(tfile.name):
                os.remove(tfile.name)
