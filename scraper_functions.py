"""
Book Data Retrieval
=============================
Author: Udit Kumar Chatterjee
Email: quantumudit@gmail.com
=============================

This module provides a class retrieving book data from the Ebooks API.
The methods defined in the class is used to fetch and manipulate book data
from the Ebooks API in a convenient way.
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
    book_id : Optional[str]
        The ID of the book.
    book_title : Optional[str]
        The title of the book.
    publication_year : Optional[int]
        The year of publication of the book.
    price : Optional[str]
        The price of the book.
    authors : Optional[str]
        The authors of the book.
    book_url : Optional[str]
        The URL of the book.
    book_image_url : Optional[str]
        The URL of the book's image.
    """
    book_id: Optional[str]
    book_title: Optional[str]
    publication_year: Optional[int]
    price: Optional[str]
    authors: Optional[str]
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
    authors = ""
    authors_data = book.get("authors")
    if authors_data is not None:
        authors = ", ".join([x.get("name") for x in authors_data])

    book_url = urljoin(website_url, book.get("book_url"))

    book_details = Book(
        book_id=book.get("id"),
        book_title=book.get("title"),
        publication_year=book.get("publication_year"),
        price=book.get("price"),
        authors=authors,
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
    popular_cat_dict: Dict[str, int] = {}
    fiction_cat_dict: Dict[str, int] = {}
    non_fiction_cat_dict: Dict[str, int] = {}

    params = (
        ("CountryCode", "US"),
        ("subjectID", "184")
    )
    api_base_url = "https://www.ebooks.com/api/subject/menu/"
    user_agent = UserAgent()
    dynamic_ua_headers = {
        "User-Agent": user_agent.random, "accept-language": "en-US"}
    timeout = 100

    response = requests.get(
        url=api_base_url, headers=dynamic_ua_headers, params=params, timeout=timeout
    )
    json_response = response.json()

    popular_subjects_category = json_response["subject_menus"][1]["subject_menu_entries"]
    fiction_category = json_response["subject_menus"][2]["subject_menu_entries"]
    non_fiction_category = json_response["subject_menus"][3]["subject_menu_entries"]

    for topic in popular_subjects_category:
        popular_cat_dict[topic["subject_name"]] = topic["id"]

    for topic in fiction_category:
        fiction_cat_dict[topic["subject_name"]] = topic["id"]

    for topic in non_fiction_category:
        non_fiction_cat_dict[topic["subject_name"]] = topic["id"]

    return [popular_cat_dict, fiction_cat_dict, non_fiction_cat_dict]


def get_topics(subject_id: int) -> Dict[str, int]:
    """Retrieve the topics for a given subject ID from the Ebooks API.

    Args:
        subject_id (int): The ID of the subject.

    Returns:
        Dict[str, int]: A dictionary containing the topics.
        Each topic name is a key and the corresponding topic ID is the value.
    """
    topics_dict: Dict[str, int] = {}

    params = (
        ("CountryCode", "US"),
        ("subjectID", str(subject_id))
    )
    api_base_url = "https://www.ebooks.com/api/subject/menu/"
    user_agent = UserAgent()
    dynamic_ua_headers = {
        "User-Agent": user_agent.random,
        "accept-language": "en-US"
    }
    timeout = 100
    response = requests.get(
        url=api_base_url, headers=dynamic_ua_headers, params=params, timeout=timeout
    )
    subject_menus = response.json().get("subject_menus")
    all_topics = subject_menus[0].get("subject_menu_entries")

    for topic in all_topics:
        topics_dict[topic.get("subject_name")] = topic.get("id")

    return topics_dict


def total_books_present(subject_id: int) -> int:
    """
    Retrieve the total number of books present for a given subject ID from the Ebooks API.

    Args:
        subject_id (int): The ID of the subject.

    Returns:
        int: The total number of books present.
    """
    params = (
        ("pageNumber", "1"),
        ("CountryCode", "US"),
        ("subjectID", str(subject_id))
    )
    api_base_url = "https://www.ebooks.com/api/search/subject/"
    user_agent = UserAgent()
    dynamic_ua_headers = {
        "User-Agent": user_agent.random,
        "accept-language": "en-US"
    }
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

    params = (
        ("pageNumber", str(page_num)),
        ("CountryCode", "US"),
        ("subjectID", str(subject_id))
    )
    api_base_url = "https://www.ebooks.com/api/search/subject/"
    user_agent = UserAgent()
    dynamic_ua_headers = {
        "User-Agent": user_agent.random, "accept-language": "en-US"}
    timeout = 100
    response = requests.get(
        url=api_base_url, headers=dynamic_ua_headers, params=params, timeout=timeout)
    books_data = response.json().get("books")

    return books_data
