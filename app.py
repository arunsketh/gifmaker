import os
import streamlit as st
from moviepy.editor import VideoFileClip

# ---------- Security: simple password gate ----------
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_ok"] = True
        else:
            st.session_state["password_ok"] = False
            st.error("Incorrect password")

    if "password_ok" not in st.session_state:
        st.text_input("Enter app password", type="password",
                      on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_ok"]:
        st.text_input("Enter app password", type="password",
                      on_change=password_entered, key="password")
        return False
    return True

if not check_password():
    st.stop()

# ---------- App UI ----------
st.set_page_config(page_title="AVI → GIF Converter", layout="centered")

st.title("AVI to GIF Converter")
st.write("Upload an AVI file, tweak options, and download the generated GIF.")

uploaded_file = st.file_uploader("Upload AVI file", type=["avi"])

col1, col2 = st.columns(2)
with col1:
    fps = st.slider("Frames per second", 1, 30, 10)
    width = st.number_input("Output width (px, 0 = original)", min_value=0, value=0)
with col2:
    start_time = st.number_input("Start time (seconds)", min_value=0.0, value=0.0, step=0.5)
    end_time = st.number_input("End time (seconds, 0 = to end)", min_value=0.0, value=0.0, step=0.5)

loop = st.slider("Loop count (0 = infinite)", min_value=0, max_value=20, value=0)
optimize = st.checkbox("Optimize GIF (smaller file, may take longer)", value=True)

convert_btn = st.button("Convert to GIF")

if uploaded_file and convert_btn:
    with st.spinner("Converting... this may take a moment."):
        # Save uploaded video to a temp file
        input_path = "input.avi"
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        clip = VideoFileClip(input_path)

        # Trim
        duration = clip.duration
        t_start = max(0, start_time)
        t_end = duration if end_time <= 0 else min(end_time, duration)
        if t_end > t_start:
            clip = clip.subclip(t_start, t_end)

        # Resize
        if width > 0:
            clip = clip.resize(width=width)

        # Apply FPS
        clip = clip.set_fps(fps)

        # Output path
        output_path = "output.gif"

        # MoviePy GIF export
        clip.write_gif(
            output_path,
            program="ImageMagick",  # or "ffmpeg" if configured
            loop=loop,
            opt=optimize
        )

        # Load GIF bytes
        with open(output_path, "rb") as f:
            gif_bytes = f.read()

        st.success("Conversion complete!")
        st.image(gif_bytes)
        st.download_button(
            label="Download GIF",
            data=gif_bytes,
            file_name=os.path.splitext(uploaded_file.name)[0] + ".gif",
            mime="image/gif",
        )

        # Clean up
        clip.close()
        os.remove(input_path)
        os.remove(output_path)
