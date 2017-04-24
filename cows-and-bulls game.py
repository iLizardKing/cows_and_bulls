from random import randint
from tkinter import *

DIGIT_COUNT_MIN = 2
DIGIT_COUNT_MAX = 10


class Model:
    def __init__(self):
        self.bull = 0  # Coincides digit, but not a place
        self.cow = 0  # Coincides digit and a place
        self.digit_num = 3
        self.user_number = None
        self.sec_number = None
        self.sec_number_list = []
        self.win = False
        self.round = 1
        self.wrong_answers = []

    def generate_digit(self):
        self.sec_number = randint(0, 10**self.digit_num - 1)
        self.sec_number_list = []
        for d in range(1, self.digit_num + 1):
            self.sec_number_list.append(
                self.sec_number % (10 ** d) // 10 ** (d - 1)
            )

    def estimate_value(self, user_number):
        self.bull = 0
        self.cow = 0
        sec_number_list = self.sec_number_list[:]
        self.user_number = user_number
        user_number_list = []
        n = len(str(self.user_number))
        for d in range(n):
            user_number_list.append(self.user_number % (10 ** (d + 1)) // 10 ** d)
        index_del = []
        # Counting the matching
        for i in range(n):
            if user_number_list[i] == sec_number_list[i]:
                self.cow += 1
                index_del.append(i)
        # Delete the matching
        sec_number_list = [sec_number_list[i] for i in range(n) if i not in index_del]
        user_number_list = [user_number_list[i] for i in range(n) if i not in index_del]
        # Counting the coincidences
        for i in range(len(user_number_list)):
            if user_number_list[i] in sec_number_list:
                self.bull += 1
                sec_number_list[sec_number_list.index(user_number_list[i])] = None

    def is_win(self, user_number):
        self.user_number = user_number
        if str(self.sec_number).zfill(self.digit_num) == \
                str(self.user_number).zfill(self.digit_num):
            self.win = True
        else:
            self.win = False
        return self.win

    def start_game(self, digit_num=3):
        self.win = False
        if digit_num in range(DIGIT_COUNT_MIN, DIGIT_COUNT_MAX + 1):
            self.digit_num = digit_num
            self.generate_digit()
        self.round = 1


class Controller:
    def __init__(self, model):
        self.model = model

    def set_view(self, view):
        self.view = view

    def start_game(self):
        digit_num = self.view.get_game_settings()
        self.model.start_game(digit_num)
        self.view.start_game()

    def input_digit(self, event=None):
        digit = self.view.get_digit()
        if digit:
            self.model.wrong_answers.append(int(digit))
            if not self.model.is_win(digit):
                self.model.estimate_value(digit)
                self.view.log_wrong_answ()
                self.model.round += 1
            else:
                self.view.game_over()


class TkView(Frame):
    font1 = ('Consolas', 14)
    font2 = ('Consolas', 16)
    font3 = ('Consolas', 18, 'bold')

    def __init__(self, controller=None, model=None, master=None, **config):
        super().__init__(master)
        self.pack(expand=True, fill='both')
        self.model = model
        self.controller = controller
        self.controller.set_view(self)
        self.create_widgets()

    def create_widgets(self):
        # top frame with probably var
        frame_top = Frame(self)
        self.digit_var = StringVar(frame_top)
        self.digit_var.trace('w', lambda name, index, mode, sv=self.digit_var.trace:
                             self.input_control(sv))
        self.answer_ent = Entry(frame_top,
                                textvariable=self.digit_var,
                                state='disabled',
                                font= __class__.font3)
        self.answer_ent.bind('<Return>', self.controller.input_digit)
        self.answer_but = Button(frame_top,
                                 text='OK',
                                 command=self.controller.input_digit,
                                 bg='#bed6be',
                                 state='disabled',
                                 font=__class__.font3)
        # log
        frame_log_parent = Frame(self)
        frame_log_child = Frame(frame_log_parent)
        self.log_txt = Text(frame_log_child,
                            wrap='word',
                            width=20,
                            height=10,
                            state='disabled',
                            font=__class__.font1)
        scrollbar = Scrollbar(frame_log_child,
                              command=self.log_txt.yview)
        self.log_txt.config(yscrollcommand=scrollbar.set)
        self.log_line = 1
        # bottom frame with settings
        frame_bottom_parent = Frame(self, bg='grey')
        frame_bottom_child = Frame(frame_bottom_parent, bg='grey')
        start_but = Button(frame_bottom_child,
                           text='START',
                           command=self.controller.start_game,
                           bg='#ffddaa',
                           font=__class__.font3)
        label = Label(frame_bottom_child,
                      text='Number of digits:',
                      bg='grey',
                      font=__class__.font2)
        self.digit_count_var = StringVar()
        self.digit_count_var.set(4)
        spinbox = Spinbox(frame_bottom_child,
                          textvariable=self.digit_count_var,
                          from_=DIGIT_COUNT_MIN, to=DIGIT_COUNT_MAX,
                          width=3,
                          font=__class__.font3)
        # packed
        frame_top.pack(side='top', fill='x', pady=5, padx=5)
        self.answer_ent.pack(side='left', expand='yes', fill='both')
        self.answer_but.pack(side='right')
        frame_log_parent.pack(fill='both', expand=True)
        frame_log_child.pack(fill='both', expand=True, padx=5)
        self.log_txt.pack(side='left', expand='yes', fill='both')
        scrollbar.pack(side='right', fill='y')
        frame_bottom_parent.pack(side='bottom', fill='x')
        frame_bottom_child.pack(fill='x', padx=5, pady=5)
        start_but.pack(side='top', fill='x')
        label.pack(side='left', expand='yes', fill='x', pady=5)
        spinbox.pack(side='left', pady=5)

    def get_game_settings(self):
        return int(self.digit_count_var.get())

    def input_control(self, event):
        if self.digit_var.get():
            st = self.digit_var.get()
            if not st[-1].isdigit():
                st = st[:-1]
                self.digit_var.set(st)

    def get_digit(self):
        digit = self.digit_var.get()
        if digit:
            if len(digit) == self.model.digit_num:
                if int(digit) in self.model.wrong_answers:
                    self.answer_ent.config(bg='blue')
                    self.answer_ent.after(500, lambda: self.answer_ent.config(bg='white'))
                else:
                    self.answer_ent.delete(0, 'end')
                    return int(digit)
            else:
                self.answer_ent.config(bg='red')
                self.answer_ent.after(500, lambda: self.answer_ent.config(bg='white'))

    def add_to_log(self, string):
        self.log_txt.config(state='normal')
        self.log_txt.insert('{}.{}'.format(self.log_line, 0), string)
        self.log_txt.config(state='disabled')
        self.log_txt.see('{0}.{1}'.format(self.log_line, 0))
        self.log_line += 1

    def log_wrong_answ(self):
        template = '\n{}. {}:   cows-{} & bulls-{}'
        message = template.format(str(self.model.round).rjust(2),
                                  self.model.user_number,
                                  self.model.cow,
                                  self.model.bull)
        self.add_to_log(message)

    def game_over(self):
        self.answer_but.config(state='disabled')
        self.answer_ent.config(state='disabled')
        message = '\nCorrect! You find the secret number {} with {} try.'. \
            format(self.model.sec_number, self.model.round)
        self.add_to_log(message)

    def start_game(self):
        self.log_line = 1
        self.log_txt.config(state='normal')
        self.log_txt.delete('1.0', 'end')
        self.log_txt.config(state='disabled')
        self.answer_but.config(state='normal')
        self.answer_ent.config(state='normal')
        message = 'Conceive {}-valued secret number, try to guess!'. \
            format(self.model.digit_num)
        self.add_to_log(message)


game_model = Model()
game_controller = Controller(game_model)
root = Tk()
root.title('Cows & Bulls')
root.minsize(width=330, height=385)
game_view = TkView(master=root,
                   controller=game_controller,
                   model=game_model)
game_view.mainloop()
