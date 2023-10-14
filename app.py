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

import time

import pandas as pd
import streamlit as st
from PIL import Image

from scraper_functions import (get_books_data, get_category_subjects,
                               get_topics, parse_books_data,
                               total_books_present)

# page configs
st.set_page_config(
    page_title="EBooks Data Extractor",
    page_icon="📖",
    layout="wide",
    menu_items=None,
    initial_sidebar_state="collapsed"
)

# image paths
logo_image = Image.open("./images/ebooks_logo.png")
books_image = Image.open("./images/books_image.jpg")

# get logo_image dimensions
original_width, original_height = logo_image.size

# Define the new width for logo
NEW_WIDTH = 700

# Calculate the new height to maintain the aspect ratio
new_height = int((NEW_WIDTH / original_width) * original_height)

# show resized logo
new_logo_image = logo_image.resize((NEW_WIDTH, new_height))
st.image(new_logo_image, use_column_width=False)


# creating 2 columns sections
col1, col2 = st.columns([0.45, 0.55], gap="medium")

with col1:
    st.image(books_image, use_column_width=True)

    st.write(
        """The application employs web scraping techniques to fetch ebook details
        from **[:blue[eBooks]](https://www.ebooks.com/)** website.
        It then generates a downloadable CSV file for users.""")

    st.write("""To initiate the process, users select a category,
    a subject, and, if available, a topic. The application then uses
    these selections to scrape the data tailored to the user's preferences.""")


with col2:
    subject_details = get_category_subjects()
    all_subjects_dict = {
        key: value for d in subject_details for key, value in d.items()}

    category_select = st.selectbox(
        'Choose a Category:',
        ('Popular Subjects', 'Fiction', 'Non-Fiction'))

    if category_select == "Popular Subjects":
        subject_select = st.selectbox(
            "Choose a Subject:", tuple(subject_details[0].keys()))
    elif category_select == "Fiction":
        subject_select = st.selectbox(
            "Choose a Subject:", tuple(subject_details[1].keys()))
    else:
        subject_select = st.selectbox(
            "Choose a Subject:", tuple(subject_details[2].keys()))

    if subject_select is not None:
        topics_details = get_topics(
            subject_id=all_subjects_dict.get(subject_select, 0))
    else:
        topics_details = get_topics(subject_id=0)

    topic_select = st.selectbox(
        "Choose a Topic:",
        tuple(topics_details.keys()))

    submit = st.button("Get Data")

    if submit:
        if len(topics_details) == 0:
            topic_id = all_subjects_dict.get(
                subject_select, None)  # type: ignore
        else:
            topic_id = topics_details.get(topic_select, None)  # type: ignore

        PAGE_NUM = 1
        all_books_details = []
        total_books_available = total_books_present(subject_id=topic_id)

        PROGRESS_TEXT = "Operation in progress. Please wait..."
        my_bar = st.progress(0, text=PROGRESS_TEXT)

        while True:
            books_data = get_books_data(page_num=PAGE_NUM, subject_id=topic_id)
            if books_data is not None and len(books_data) > 0:
                for book in books_data:
                    details = parse_books_data(book)
                    details["page_num"] = PAGE_NUM
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

        if len(all_books_details) == 0:
            st.write("No books available to collect")
        else:
            books_df = pd.DataFrame(all_books_details)
            csv_file = books_df.to_csv().encode("utf-8")

            st.download_button(
                label="Download Data as CSV",
                data=csv_file,
                file_name="books_data.csv",
                mime="text/csv"
            )
