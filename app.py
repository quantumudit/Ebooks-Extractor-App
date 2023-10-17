"""
Ebooks Data Extractor Script
=============================
Author: Udit Kumar Chatterjee
Email: quantumudit@gmail.com
=============================

The code is a Streamlit application that allows users to select a category, subject, and topic,
and then scrape ebook data from the eBooks.com website.
It retrieves the data based on the user's selections and
generates a downloadable CSV file containing the ebook information.
"""

# Import necessary libraries
import time
from datetime import datetime

import pandas as pd
import streamlit as st
from PIL import Image

import scraper_util as su

# Configure the Streamlit page
st.set_page_config(
    page_title="EBooks Data Extractor",
    page_icon="📖",
    layout="wide",
    menu_items=None,
    initial_sidebar_state="collapsed"
)

# Define paths for images
logo_image = Image.open("./images/ebooks_logo.png")
books_image = Image.open("./images/books_image.jpg")

# Get the dimensions of the logo_image
original_width, original_height = logo_image.size

# Define the new width for the logo
NEW_WIDTH = 700

# Calculate the new height to maintain the aspect ratio
new_height = int((NEW_WIDTH / original_width) * original_height)

# Display the resized logo
new_logo_image = logo_image.resize((NEW_WIDTH, new_height))
st.image(new_logo_image, use_column_width=False)

# Create two columns for layout
col1, col2 = st.columns([0.45, 0.55], gap="medium")

# Populate col1 with image and project information
with col1:
    st.image(books_image, use_column_width=True)
    st.write(
        """The application employs web scraping techniques to fetch ebook details
        from **[:blue[eBooks]](https://www.ebooks.com/)** website.
        It then generates a downloadable CSV file for users."""
    )
    st.write(
        """To initiate the process, users select a category,
        a subject, and, if available, a topic. The application then uses
        these selections to scrape the data tailored to the user's preferences."""
    )

# Populate col2 with interactive elements
with col2:
    # Retrieve subject details for the available categories
    subject_details = su.get_category_subjects()
    all_subjects_dict = {
        sub_name: sub_id for d in subject_details for sub_name, sub_id in d.items()}

    # User selects a category
    category_select = st.selectbox(
        'Choose a Category:',
        ('Popular Subjects', 'Fiction', 'Non-Fiction')
    )

    # User selects a subject based on the chosen category
    if category_select == "Popular Subjects":
        subject_select = st.selectbox(
            "Choose a Subject:", tuple(subject_details[0].keys()))
    elif category_select == "Fiction":
        subject_select = st.selectbox(
            "Choose a Subject:", tuple(subject_details[1].keys()))
    else:
        subject_select = st.selectbox(
            "Choose a Subject:", tuple(subject_details[2].keys()))

    # Retrieve topics for the selected subject
    topics_details = su.get_topics_for_subject(
        subject_id=all_subjects_dict.get(subject_select))

    # User selects a topic (if available) based on the selected subject
    topic_select = st.selectbox(
        "Choose a Topic:",
        tuple(topics_details.keys()))

    # Create a button to initiate data extraction
    submit = st.button("Get Data")

    if submit:
        # Determine the topic_id (subject_id if no topics available)
        if len(topics_details) == 0:
            topic_id = all_subjects_dict.get(subject_select)
        else:
            topic_id = topics_details.get(topic_select)

        # Initialize page number and an empty list for book details
        PAGE_NUM = 1
        all_books_details = []

        # Get the total number of books available for the topic
        total_books_available = su.fetch_total_books_count(subject_id=topic_id)

        # Create a progress bar for data extraction
        PROGRESS_TEXT = "Operation in progress. Please wait..."
        my_bar = st.progress(0, text=PROGRESS_TEXT)

        while True:
            books_data = su.fetch_books_data(
                page_num=PAGE_NUM, subject_id=topic_id)
            if books_data is not None and len(books_data) > 0:
                for book in books_data:
                    details = su.parse_books_details(book)
                    details["scrape_timestamp"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")
                    all_books_details.append(details)

                time.sleep(1)

                PAGE_NUM += 1

                progress_pct = int(
                    (len(all_books_details) / total_books_available) * 100)

                my_bar.progress(
                    min(progress_pct, 100),
                    text=(
                        f"Books Collected: {len(all_books_details)} "
                        f"out of {total_books_available} | {progress_pct}%"
                    )
                )
            else:
                break

        # Generate a CSV file for user download
        if len(all_books_details) == 0:
            st.write("No books available to collect")
        else:
            books_df = pd.DataFrame(all_books_details)
            BOOKS_DATA_CSV = books_df.to_csv(index=False, encoding='utf-8')

            st.download_button(
                label="Download Data as CSV",
                data=BOOKS_DATA_CSV,
                file_name="books_data.csv",
                mime="text/csv"
            )
