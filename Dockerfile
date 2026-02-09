# Use a lightweight Python image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Verification Step ---
# Print the installed version of the library to the build logs for debugging.
RUN pip show google-generativeai

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]