import json
from bs4 import BeautifulSoup


class NoQuestionFound(Exception):
    pass


class Parser:
    """
    Handles heavy parsing tasks
    Doesn't really need to be a class but it looks better this way :)
    """
    def __init__(self):
        pass

    def parse(self, page: str):
        """
        takes a page, finds the javascript tags
        parses question data in a crud but effective mash up of splits and indexing
        finds: qid, qnum, type
        """
        tags = self.find_tags(page)
        try:
            x = tags[-1].text.split('\n')
            x = [i for i in x if '=' in i]
            question = x[1].split('{')[1:]
            _json = '{' + '{'.join(question).strip(';\n')
            _json = json.loads(_json)
        except BaseException:
            raise NoQuestionFound()

        qid = _json['id']
        type_ = _json['answer']['type']
        qnum = x[3].split('=')[-1].strip(';\n').strip(' ')
        return {'qid': qid, 'qnum': qnum}, type_

    @staticmethod
    def find_tags(page: str):
        """
        uses bs4 to parse tags
        """
        soup = BeautifulSoup(page, 'html.parser')
        return soup.find_all('script', type="text/javascript")
