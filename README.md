# bookr# Bookr
- Bookr is a 2-sided platform which makes it easy to attend and run events
- Customers who want an easy, fast, reliable way to discover and book events
- Businesses who need a simple system to post their events, draw attendees to them, and manage and share event information easily
- Current event booking systems are often expensive, hard to use, can have outdated attendance info, and may cause businesses to scatter their event information across different sites
- Bookr centralises all information so that event information is clear, bookings are easily tracked, and capacity is accurate
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


## Run tests

To run the automated tests for the project, use:

python manage.py test

This will run the test suite and check that the main parts of the application are working correctly.



## Notes

- Make sure you are in the project root folder before running the commands.
- The Conda environment must be activated each time before running the project.
