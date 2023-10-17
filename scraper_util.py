"""
Data Scraping Utility Functions
===============================
Author: Udit Kumar Chatterjee
Email: quantumudit@gmail.com
===============================

This module provides a class retrieving book data from the Ebooks API.
The functions defined is used to fetch and manipulate book data
from the Ebooks API in a convenient way.

Functions:
----------
1. parse_books_data(): Parse book details and return as a dictionary.
2. get_category_subjects(): Retrieve category subjects from the Ebooks API.
3. get_topics(): Retrieve topics for a given subject ID.
4. total_books_present(): Retrieve the total number of books for a subject.
5. get_books_data(): Retrieve books data for a page and subject.

"""


from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from fake_useragent import UserAgent


@dataclass
class Book:
    """
    A class to represent a book.

    Attributes:
    -----------
    book_id: The ID of the book.
    book_title: The title of the book.
    book_subtitle: The subtitle of the book.
    book_description: The description of the book.
    publisher: The publisher of the book.
    edition: The edition of the book.
    publication_date: The date of publication of the book.
    publication_month_year: The month and year of publication of the book.
    publication_year: The year of publication of the book.
    price: The price of the book in USD.
    prime_authors: The primary/main authors of the book.
    num_authors: The number of authors of the book.
    book_url: The URL of the book.
    book_image_url: The URL of the book's image.
    """
    book_id: Optional[str]
    book_title: Optional[str]
    book_subtitle: Optional[str]
    book_description: Optional[str]
    publisher: Optional[str]
    edition: Optional[str]
    publication_date: Optional[str]
    publication_month_year: Optional[str]
    publication_year: Optional[int]
    price: Optional[str]
    prime_authors: Optional[str]
    num_authors: Optional[int]
    book_url: Optional[str]
    book_image_url: Optional[str]


def parse_books_data(book: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the details of a book and return them as a dictionary.

    Args:
        book (Dict[str, Any]): A dictionary containing the details of the book.

    Returns:
        Dict[str, Any]: A dictionary containing the parsed details of the book.
    """
    website_url = "https://www.ebooks.com/"
    authors_data = book.get("authors")
    authors = ", ".join([author.get("name")
                        for author in authors_data]) if authors_data else ""

    book_url = urljoin(website_url, book.get("book_url"))

    book_details = Book(
        book_id=book.get("id"),
        book_title=book.get("title"),
        book_subtitle=book.get("subtitle"),
        book_description=book.get("description"),
        publisher=book.get("publisher"),
        edition=book.get("edition"),
        publication_date=book.get("on_sale_date"),
        publication_month_year=book.get("short_publication_date"),
        publication_year=book.get("publication_year"),
        price=book.get("price"),
        prime_authors=authors if authors else "Unknown",
        num_authors=book.get("num_authors"),
        book_url=book_url,
        book_image_url=book.get("image_url")
    )

    return asdict(book_details)


def get_category_subjects() -> List[Dict[str, int]]:
    """
    Retrieve the category subjects from the Ebooks API.

    Returns:
        A list of dictionaries containing the category subjects.
        Each dictionary contains the subject name as the key
        and the subject ID as the value.
    """
    def fetch_category_subjects(item_idx: int) -> Dict[str, int]:
        params = [("CountryCode", "US"), ("subjectID", 184)]
        api_base_url = "https://www.ebooks.com/api/subject/menu/"
        user_agent = UserAgent()
        dynamic_ua_headers = {
            "User-Agent": user_agent.random, "accept-language": "en-US"}
        timeout = 100

        response = requests.get(
            url=api_base_url, headers=dynamic_ua_headers, params=params, timeout=timeout)
        subject_entries = response.json(
        )["subject_menus"][item_idx]["subject_menu_entries"]
        return {entry["subject_name"]: entry["id"] for entry in subject_entries}

    popular_cat_dict = fetch_category_subjects(item_idx=1)
    fiction_cat_dict = fetch_category_subjects(item_idx=2)
    non_fiction_cat_dict = fetch_category_subjects(item_idx=3)

    return [popular_cat_dict, fiction_cat_dict, non_fiction_cat_dict]


def get_topics(subject_id: int) -> Dict[str, int]:
    """Retrieve the topics for a given subject ID from the Ebooks API.

    Args:
        subject_id (int): The ID of the subject.

    Returns:
        Dict[str, int]: A dictionary containing the topics.
        Each topic name is a key and the corresponding topic ID is the value.
    """
    def fetch_topics(subject_id: int) -> Dict[str, int]:
        params = [("CountryCode", "US"), ("subjectID", str(subject_id))]
        api_base_url = "https://www.ebooks.com/api/subject/menu/"
        user_agent = UserAgent()
        dynamic_ua_headers = {
            "User-Agent": user_agent.random, "accept-language": "en-US"}
        timeout = 100

        response = requests.get(
            url=api_base_url, headers=dynamic_ua_headers, params=params, timeout=timeout)
        subject_menu = response.json().get("subject_menus")
        return {entry["subject_name"]: entry["id"]
                for entry in subject_menu[0]["subject_menu_entries"]}

    return fetch_topics(subject_id)


def total_books_present(subject_id: int) -> int:
    """
    Retrieve the total number of books present for a given subject ID from the Ebooks API.

    Args:
        subject_id (int): The ID of the subject.

    Returns:
        int: The total number of books present.
    """
    params = [
        ("pageNumber", "1"),
        ("CountryCode", "US"),
        ("subjectID", str(subject_id))]
    api_base_url = "https://www.ebooks.com/api/search/subject/"
    user_agent = UserAgent()
    dynamic_ua_headers = {
        "User-Agent": user_agent.random, "accept-language": "en-US"}
    timeout = 100

    response = requests.get(
        url=api_base_url, headers=dynamic_ua_headers, params=params, timeout=timeout)
    total_books = response.json().get("total_results")
    return int(total_books)


def get_books_data(page_num: int, subject_id: int) -> Optional[List[Dict]]:
    """Retrieve the books data for a given page number and subject ID from the Ebooks API.

    Args:
        page_num (int): The page number of the books data to retrieve.
        subject_id (int): The ID of the subject.

    Returns:
        Optional[List[Dict]]: A list of dictionaries containing the books data.
        Returns `None` if no books data is found.
    """
    params = [
        ("pageNumber", str(page_num)),
        ("CountryCode", "US"),
        ("subjectID", str(subject_id))]
    api_base_url = "https://www.ebooks.com/api/search/subject/"
    user_agent = UserAgent()
    dynamic_ua_headers = {
        "User-Agent": user_agent.random, "accept-language": "en-US"}
    timeout = 100

    response = requests.get(
        url=api_base_url, headers=dynamic_ua_headers, params=params, timeout=timeout)
    books_data = response.json().get("books")

    return books_data
