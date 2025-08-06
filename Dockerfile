# Step 1: Use an official Python runtime as a parent image
FROM python:3.11-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements file into the container
# This is done first to leverage Docker's layer caching, which speeds up future builds.
COPY requirements.txt .

# Step 4: Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application's code into the container
COPY . .

# Step 6: Expose the port Streamlit runs on
EXPOSE 8501

# Step 7: Define the command to run your app when the container starts
CMD ["streamlit", "run", "app.py"]