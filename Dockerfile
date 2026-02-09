# Use a lightweight Python image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .

# --- Force Clean Installation ---
# Upgrade pip, uninstall any old version of the library to break caches, then install fresh.
RUN python -m pip install --upgrade pip && \
    pip uninstall -y google-generativeai || true && \
    pip install --no-cache-dir -r requirements.txt

# --- Verification Step ---
# Print the installed version of the library to the build logs for debugging.
RUN echo "Verifying google-generativeai installation..." && \
    python -c "import google.generativeai as genai; print(f'google-generativeai version: {genai.__version__}')"
# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]