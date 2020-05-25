import functools
import json
import sys
from statistics import mean

from parser_utils import Parser, NoQuestionFound, AAID_REGEX, FIND_DIGIT_REGEX


class InvalidURLException(BaseException):
    def __init__(self, url, *args):
        self.__url = url
        super().__init__(*args)

    def __str__(self):
        return f"Invalid URL {self.__url}"


def catch(func):
    @functools.wraps(func)
    def stub(self, *args, **kwargs):
        try:
            return func(self, *args, *kwargs)
        except NoQuestionFound:  # raised in parser, questions finished
            return True, True
        except KeyboardInterrupt:
            sys.exit()  # quits script
        except BaseException as e:
            return None, e

    return stub


class AnswerHandler:
    """
    handles all the answer logic
    """

    def __init__(self, session):
        self.sesh = session
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                      ' Chrome/71.0.3578.98 Safari/537.36'}
        self.process_ans_url = 'https://www.drfrostmaths.com/homework/process-answer.php'
        self.answer_functions = {'expression': self.answer_expression,
                                 'numeric': self.answer_numeric,
                                 'eqnsolutions': self.answer_eqnsolutions,
                                 'coordinate': self.answer_coordinate,
                                 'multiplechoice': self.answer_multiplechoice,
                                 'textual': self.answer_textual,
                                 'fraction': self.answer_fraction,
                                 'vector': self.answer_vector,
                                 'table': self.answer_table,
                                 'shape': self.answer_shape,
                                 'list': self.answer_list,
                                 'standardform': self.answer_standardform}

    @catch
    def answer_questions(self, url: str):
        """
        main loop answers questions util an error is raised
        due to no more questions, invalid input or connection errors.

        Decorator handles returns.

        Answer process:

        - Post deliberately wrong answer without aaid i.e. {'qid': 1228, 'qnum': 1, 'expression-answer-1': 1}.
        - Sever sends correct answer without registering an attempt as no aaid was associated with the request.
        - Parse response for answer, use appropriate function.
        - Send answer with aaid i.e. {'qid': 1228, 'qnum': 1, 'expression-answer-1': "parsed answer", aaid: 12848}.
        - question answered!

        repeat.
        """

        try:
            aaid = FIND_DIGIT_REGEX.findall(AAID_REGEX.findall(url)[0])[0]
        except IndexError:
            raise InvalidURLException(url)

        while True:  # main loop
            # remove &qnum=NUMBER in case already appended
            page = self.sesh.get("".join(url.split("&qnum=")[:1]), headers=self.headers).text  # get question page
            data, type_ = Parser.parse(page)  # parse question data
            answer = self.find_answer(data, type_)  # retrieve answer to question
            data['aaid'] = aaid
            try:
                result = self.answer_functions[type_](data, answer)  # select appropriate function to process answer
            except KeyError:
                self.new_type(answer, type_)  # not implemented type
                continue  # skips auto submit

            self.submit(result)

    def find_answer(self, data: dict, type_: str):
        """
        Attempts to find the correct answer to the current question.

        :param data: request payload
        :param type_: answer type
        :return: correct answer string
        """
        data = dict(data)
        data[f'{type_}-answer-1'] = '1'  # prepare incorrect  answer
        print(f'Question number: {data["qnum"]}', '|', f'Question type: {type_}')
        r = self.sesh.post(self.process_ans_url, data=data, headers=self.headers)  # submit incorrect answer
        _json = json.loads(r.text)
        return _json['answer']  # parse correct answer

    def submit(self, data: dict):
        # noinspection PyBroadException
        try:
            r = self.sesh.post(self.process_ans_url, data=data, timeout=3)
        except BaseException:
            return False

        _json = json.loads(r.text)
        if not _json['isCorrect']:
            self.wrong_answer(_json, data)
            return False
        return True

    @staticmethod
    def new_type(answer: dict, type_: str):
        print(f'No system in place to auto submit this answer type ({type_}) yet you will have to type it in manually:'
              f'\n {answer}')
        input('Press enter to proceed: ')

    @staticmethod
    def wrong_answer(response, data: dict):
        print('-- The wrong answer was submitted --')
        print('The following data if for debugging:')
        print(f'Request: {data}')
        print(f'Response: {response}')

    # answer specific functions --:

    @staticmethod
    def answer_expression(data, answer):
        answer = [answer['main']]
        data['expression-answer'] = answer
        return data

    @staticmethod
    def answer_numeric(data, answer):
        for index, item in enumerate(answer):
            if item['exact']:
                data[f'numeric-answer-{index + 1}'] = item['exact']
            else:
                # find mid value
                data[f'numeric-answer-{index + 1}'] = mean([float(item["to"]), float(item["from"])])
        return data

    @staticmethod
    def answer_eqnsolutions(data, answer):
        data['eqnsolutions-answer'] = str(answer).replace("'", '"').replace(' ', '')
        return data

    @staticmethod
    def answer_coordinate(data, answer):
        data['expression-answer-x'] = answer['x']
        data['expression-answer-y'] = answer['y']
        return data

    @staticmethod
    def answer_multiplechoice(data, answer):
        data['multiplechoice-answer[]'] = answer
        return data

    @staticmethod
    def answer_textual(data, answer):
        for index, item in enumerate(answer):
            data[f'textual-answer-{index + 1}'] = item
        return data

    @staticmethod
    def answer_fraction(data, answer):
        data['fraction-numer'] = answer['numer']
        data['fraction-denom'] = answer['denom']
        return data

    @staticmethod
    def answer_vector(data, answer):
        data['expression-answer-vector'] = str(answer).replace("'", '"')
        return data

    @staticmethod
    def answer_table(data, answer):
        for z, i in enumerate(answer):
            for p, x in enumerate(i):
                if x:
                    data[f'table-answer-{z + 1}-{p + 1}'] = x
        data['expression-answer-table'] = str(answer).replace("'", '"')
        return data

    @staticmethod
    def answer_shape(data, answer):
        data['shape-answer'] = str(answer).replace("'", '"').replace(' ', '')
        return data

    @staticmethod
    def answer_list(data, answer):
        ans = ','.join(answer)
        data['list-answer'] = ans
        return data

    @staticmethod
    def answer_standardform(data, answer):
        data['expression-answer-main'] = answer['main']
        data['expression-answer-power'] = answer['power']
        return data
