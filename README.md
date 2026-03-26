# bookr# Bookr

Bookr is a Django web application for discovering, creating, and booking events.

## Local Setup

### 1. Install Anaconda

Download and install Anaconda for your operating system.

### 2. Create and activate a new environment

Open a terminal in the project folder and run:

conda create -n bookr python=3.11
conda activate bookr

### 3. Install the project requirements

Install all required packages using:

pip install -r requirements.txt

### 4. Apply database migrations

Set up the database tables with:

python manage.py migrate

### 5. Populate the database

Load the sample data by running:

python populate.py

### 6. Run the development server

Start the app locally with:

python manage.py runserver

Then open the local URL shown in the terminal, usually:

http://127.0.0.1:8000/

## Notes

- Make sure you are in the project root folder before running the commands.
- The Conda environment must be activated each time before running the project.
