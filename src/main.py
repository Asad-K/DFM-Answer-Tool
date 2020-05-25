from requests import Session
from tkinter import *
import tkinter.messagebox as tm
from src.answer_handler import AnswerHandler
import traceback
import json


class InvalidLoginDetails(Exception):
    pass


class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

        self.label_username = Label(self, text="Email")
        self.label_password = Label(self, text="Password")

        self.entry_username = Entry(self)
        self.entry_password = Entry(self, show="*")

        self.label_username.grid(row=0, sticky=E)
        self.label_password.grid(row=1, sticky=E)
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        self.log_btn = Button(self, text="Login", command=self._login_btn_clicked)
        self.log_btn.grid(columnspan=2)

        self.pack()

    def _login_btn_clicked(self):
        email = self.entry_username.get()
        password = self.entry_password.get()
        if '@' not in email:
            email += '@kedst.ac.uk'
        try:
            Interface(email, password)
        except InvalidLoginDetails as e:
            print(e, file=sys.stderr)
            tm.showerror("Login error", "Incorrect Email or Password")


class Interface:
    """
    main interface between user and script
    """

    def __init__(self, email, password):
        self.session = Session()
        self.test_login(email, password)
        self.handler = AnswerHandler(self.session)
        # root.destroy()  # destroy login menu
        # self.print_init()
        # self.print_instructions()
        self.main_loop()

    def main_loop(self):
        """
        main interface loop
        will only exit if ctl-c is pressed
        """
        print('Press ctrl-c to quit')
        while True:
            # url = input('\nType Question url: ')
            url = "https://www.drfrostmaths.com/do-question.php?aaid=8890685"
            handler = AnswerHandler(self.session)
            res, err = handler.answer_questions(url)
            if res:
                print('No more questions for this URL')
            else:
                print(f'Unexpected exception occurred: {err}', file=sys.stderr)
                traceback.print_exc()

    def test_login(self, email, password):
        login_url = 'https://www.drfrostmaths.com/process-login.php?url='
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                 ' Chrome/71.0.3578.98 Safari/537.36'}
        data = {'login-email': email, 'login-password': password}
        self.session.post(login_url, headers=headers, data=data)
        try:
            """
            crude bad way of verifying authentication can be improved
            tests if user can load times tables
            """
            res = self.session.get('https://www.drfrostmaths.com/homework/process-starttimestables.php')
            json.loads(res.text)
        except BaseException:
            raise InvalidLoginDetails(f'Email: {email}, Password: {"*" * len(password)}')

    @staticmethod
    def print_init():
        print_string = '---- Dr Frost Answer Tool v3 ----\n' \
                       '----      Author: AK163631    ----\n' \
                       '*** Warning: this script has not been properly tested so might unexpectedly break ***\n' \
                       'Source: https://github.com/AK163631/DFM-Answer-Tool\n' \
                       'The author does not assume any liability for the use or abuse of this program!\n' \
                       'This tool is intended to be used to check answers\n' \
                       'Although it submit most answer types for you\n' \
                       'Release notes:\n' \
                       '    - Fixed and optimised parser'
        print(print_string)

    @staticmethod
    def print_instructions():
        print_string = "\nstep1 - Login to dfm on both the tool and web browser\n" \
                       "step2 - Navigate to a set of assessment questions on dfm usually set by a teacher\n" \
                       "Note: you can also use the tool for practice questions aswell\n" \
                       "step3 - When you start the questions you will be given a URL that look something like this:\n" \
                       "http://www.drfrostmaths.com/homework/do-question.php?aaid=590397\n" \
                       "OR like this:\n" \
                       "http://www.drfrostmaths.com/homework/do-question.php?aaid=590399&qnum=4\n" \
                       "Note: It does not make a difference if you are in the middle of a set questions or at the " \
                       "start, the program will answer remaining questions\n" \
                       "step5 - Copy the URL and paste it into the tool then press enter," \
                       "step6 - The tool will find the answer to the question you" \
                       " are currently on and print it to the screen\n" \
                       "step7 - Input this into dfm and submit it, " \
                       "some answers are auto-submitted for you just refresh the web page\n" \
                       "step8 - Press enter for the answer to the next question\n" \
                       "Note: The tool will not continue to answer the next question until" \
                       " you have submitted your answer or it has already been auto-submitted by the tool\n\n"
        choice = input('Do you wish to read the guide on how to use the tool? (y/n): ')
        if choice == 'y':
            print(print_string)


if __name__ == "__main__":
    Interface("jutibohove@datasoma.com", "pass")
    # root = Tk()
    # root.protocol('WM_DELETE_WINDOW', sys.exit)
    # root.geometry('300x80')
    # root.title('DFM Login Screen')
    # lf = LoginFrame(root)
    # # wait for login to be retrieved
    # root.mainloop()
