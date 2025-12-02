AVI to GIF Converter (Secured)

A simple, password-protected Streamlit application to convert AVI video files to GIFs with customizable options for duration, FPS, and resolution.

Features

Secure Access: Password protection ensures only authorized users can access the tool.

Customizable: Trim video segments, resize output, and adjust frame rate.

Privacy First: Configured to disable Streamlit usage statistics.

Setup Instructions

1. Local Installation

Clone this repository and navigate to the folder:

git clone <your-repo-url>
cd <your-repo-folder>


Install the requirements:

pip install -r requirements.txt


2. Configure Secrets (Important!)

Create a file named secrets.toml inside the .streamlit folder.
Note: This file is ignored by Git to protect your password.

File structure: .streamlit/secrets.toml

Content:

password = "super-secret-password"


3. Run the App

streamlit run app.py


Deployment on Streamlit Cloud

Push app.py, .gitignore, requirements.txt, and .streamlit/config.toml to GitHub.

Connect your repository to Streamlit Cloud.

In the Streamlit Cloud dashboard, go to your app's Settings > Secrets.

Paste your password configuration there:

password = "your-deployment-password"


Deploy!
