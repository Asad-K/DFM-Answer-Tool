import re
from json import JSONDecoder

from bs4 import BeautifulSoup


class NoQuestionFound(Exception):
    pass


class ParseError(Exception):
    pass


QNUM_REGEX = re.compile(r"var qnum = .+;")
FIND_DIGIT_REGEX = re.compile(r"\d+")


class Parser:
    """
    Handles parsing tasks
    """

    @staticmethod
    def parse(page: str):
        """
        takes a page, finds the javascript tags.
        Parses JSON objects from javascript to extract the qid, qnum and type
        """
        current_question_script = str(Parser.find_tags(page)[-4])
        _json = list(Parser.extract_json(current_question_script))[0]  # extract json and select first object
        qid = _json['id']
        type_ = _json['answer']['type']
        qnum = FIND_DIGIT_REGEX.findall(QNUM_REGEX.findall(current_question_script)[0])[0]  # extract question number
        return {'qid': qid, 'qnum': qnum}, type_

    @staticmethod
    def find_tags(page: str):
        """
        uses bs4 to parse tags
        """
        return BeautifulSoup(page, 'html.parser').find_all('script')

    @staticmethod
    def extract_json(string: str):
        """
        Extracts json objects from string
        """
        pos = 0
        while True:
            match = string.find('{', pos)
            if match == -1:
                break
            try:
                result, index = JSONDecoder().raw_decode(string[match:])
                yield result
                pos = match + index
            except ValueError:
                pos = match + 1
