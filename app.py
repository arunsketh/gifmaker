import os
import tempfile

import streamlit as st
from moviepy.video.io.VideoFileClip import VideoFileClip

# -----------------------------
# 1. Basic page configuration
# -----------------------------
st.set_page_config(
    page_title="AVI → GIF Converter",
    page_icon="🎞️",
    layout="centered",
)

# -----------------------------
# 2. Simple password protection
# -----------------------------
def check_password() -> bool:
    """Gate the app behind a single password stored in st.secrets."""
    def password_entered():
        pw = st.session_state.get("password", "")
        if pw == st.secrets["app_password"]:
            st.session_state["password_ok"] = True
        else:
            st.session_state["password_ok"] = False
            st.error("Incorrect password")

    if "password_ok" not in st.session_state:
        st.session_state["password_ok"] = False

    if not st.session_state["password_ok"]:
        st.text_input(
            "Enter app password",
            type="password",
            key="password",
            on_change=password_entered,
        )
        return False

    return True


if not check_password():
    st.stop()

# -----------------------------
# 3. App title and description
# -----------------------------
st.title("AVI to GIF Converter")
st.write(
    "Upload an `.avi` video, adjust the options, and download an animated GIF."
)

# -----------------------------
# 4. File upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload an AVI file",
    type=["avi"],
    help="Maximum size is controlled by Streamlit's server configuration.",
)

if uploaded_file is not None:
    st.info(f"Selected file: **{uploaded_file.name}**")

# -----------------------------
# 5. Conversion options
# -----------------------------
st.subheader("Conversion Options")

col1, col2 = st.columns(2)

with col1:
    fps = st.slider("Frames per second", min_value=1, max_value=30, value=10)
    width = st.number_input(
        "Output width (px, 0 = keep original width)",
        min_value=0,
        value=0,
        step=10,
    )

with col2:
    start_time = st.number_input(
        "Start time (seconds)", min_value=0.0, value=0.0, step=0.5
    )
    end_time = st.number_input(
        "End time (seconds, 0 = until end)",
        min_value=0.0,
        value=0.0,
        step=0.5,
    )

loop = st.slider(
    "Loop count (0 = infinite loop in most viewers)",
    min_value=0,
    max_value=20,
    value=0,
)
optimize = st.checkbox(
    "Optimize GIF (smaller file, slower to generate)", value=True
)

convert_btn = st.button("Convert to GIF", type="primary")

# -----------------------------
# 6. Conversion logic
# -----------------------------
def convert_avi_to_gif(
    uploaded_file,
    fps: int,
    width: int,
    start_time: float,
    end_time: float,
    loop: int,
    optimize: bool,
) -> bytes:
    """Convert an uploaded AVI video to a GIF and return GIF bytes."""
    # Use a temporary directory so it works on Streamlit Cloud
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.avi")
        output_path = os.path.join(tmpdir, "output.gif")

        # Save uploaded file to disk
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        # Load video
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

        # Set FPS
        clip = clip.set_fps(fps)

        # Write GIF
        clip.write_gif(
            output_path,
            fps=fps,
            loop=loop,
            opt=optimize,
        )  # MoviePy wraps imageio's GIF writer.[web:49]

        # Read back bytes
        with open(output_path, "rb") as f:
            gif_bytes = f.read()

        clip.close()

    return gif_bytes


# -----------------------------
# 7. Run conversion on click
# -----------------------------
if convert_btn:
    if uploaded_file is None:
        st.warning("Please upload an AVI file first.")
    else:
        with st.spinner("Converting to GIF..."):
            try:
                gif_bytes = convert_avi_to_gif(
                    uploaded_file=uploaded_file,
                    fps=fps,
                    width=width,
                    start_time=start_time,
                    end_time=end_time,
                    loop=loop,
                    optimize=optimize,
                )
            except Exception as e:
                st.error(f"Conversion failed: {e}")
            else:
                st.success("Conversion complete!")
                st.image(gif_bytes, caption="Preview", use_column_width=True)
                st.download_button(
                    label="Download GIF",
                    data=gif_bytes,
                    file_name=os.path.splitext(uploaded_file.name)[0] + ".gif",
                    mime="image/gif",
                )
