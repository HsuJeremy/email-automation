#!/usr/bin/python3
from bs4 import BeautifulSoup


def parse_message(message_str):
    soup = BeautifulSoup(message_str, 'html.parser')
    # print(soup.prettify())
    # print(soup.div)

    for script in soup(['script', 'style']):
        script.decompose()

    strips = list(soup.stripped_strings)
    print(strips)
