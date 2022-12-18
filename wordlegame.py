# -*- coding: utf-8 -*-
"""wordlegame.py
Sumitra Mukherjee
reply_all from https://raw.githubusercontent.com/norvig/pytudes/4bcea911eea4df8163c11b760e1270a974e4b8dd/ipynb/wordle-small.txt
"""

from urllib.request import urlopen
import functools
from collections import Counter
from numpy.random import choice
from ipywidgets import widgets
from IPython.display import display
import json

class Wordle:

    def __init__(self):
        self.word_source = 'https://raw.githubusercontent.com/norvig/pytudes/4bcea911eea4df8163c11b760e1270a974e4b8dd/ipynb/wordle-small.txt'
        self.WORDS = self.get_wordle_words()
        self.LTRS = [chr(i) for i in range(ord('A'), ord('A')+26)]
        self.nC, self.nR = 5, 6 # number of columns (letters), rows (guesses)
        self.COLOR = {'G':'lime', 'Y':'yellow', '.':'silver'}
        self.TARGET = choice(self.WORDS)
        self.C_NBR, self.G_NBR = 0, 0
        self.CELL = self.get_cell()
        self.BOARD = self.get_board()
        self.KEY = self.get_key()
        self.KEYBOARD = self.get_keyboard()
        self.MESSAGE = self.get_message()
        self.S, self.G = self.get_tree()

    @functools.lru_cache(None)
    def reply_for(self, guess, target): 
        "The five-character reply for this guess on this target in Wordle."
        # We'll start by having each reply be either Green or Miss ...
        reply = ['G' if guess[i] == target[i] else '.' for i in range(self.nC)]
        # ... then we'll change the replies that should be yellow
        counts = Counter(target[i] for i in range(self.nC) if guess[i] != target[i])
        for i in range(self.nC):
            if reply[i] == '.' and counts[guess[i]] > 0:
                counts[guess[i]] -= 1
                reply[i] = 'Y'
        return ''.join(reply)

    def get_wordle_words(self):
        with urlopen(self.word_source) as f: W = f.read().decode('utf-8').split('\n')[:-1]
        return sorted([w.upper() for w in W])

    def get_cell(self):
        layout=widgets.Layout(width='100%', height='40px', border="1px solid")
        style = {'button_color': 'white'}
        cell = {}
        for c in range(self.nC):
            for r in range(self.nR):
                cell[(c,r)] = widgets.Button(layout=layout, style = style, description = '')
        return cell

    def get_board(self):
        clist = [self.CELL[(c,r)] for r in range(6) for c in range(5)]
        layout=widgets.Layout(grid_template_columns="repeat(5, 40px)")
        board = widgets.GridBox(children=clist, layout=layout)
        return board

    def get_key(self):
        layout=widgets.Layout(width='auto', height='40px', border="1px solid")
        style = {'button_color': 'white'}
        keys = {}
        for k in self.LTRS:
            keys[k] = widgets.Button(layout=layout, style = style, description = k)
            keys[k].on_click(self.show_letter)
        style = {'button_color': 'Aqua'}
        keys['backspace'] = widgets.Button(layout=layout, style = {'button_color': 'red'}, description = chr(8592))
        keys['backspace'].on_click(self.erase_letter)
        keys['enter'] = widgets.Button(layout=layout, style = {'button_color': 'aqua'}, description = chr(9166))
        keys['enter'].on_click(self.enter_guess)
        return keys

    def get_keyboard(self):
        CHRS = []
        for k in [chr(i) for i in range(ord('A'), ord('A')+26)] + ['backspace', 'enter']:
            CHRS.append(self.KEY[k])

        layout=widgets.Layout(grid_template_columns="repeat(14, 40px)")
        keyboard = widgets.GridBox(children=CHRS, layout=layout)
        return keyboard

    def show_letter(self, b):
        self.CELL[(self.C_NBR, self.G_NBR)].description = b.description
        if self.C_NBR < 5:
            self.C_NBR += 1
        else:
            self.MESSAGE.description = 'Select enter when done with guess.'

    def erase_letter(self, b):
        nbr = max(0, self.C_NBR-1)
        self.CELL[(nbr, self.G_NBR)].description = ' '
        self.C_NBR = nbr

    def enter_guess(self, b):
        guess = ''.join([self.CELL[(c, self.G_NBR)].description for c in range(5)])
        if guess not in self.WORDS:
            self.MESSAGE.description = 'Guess is not a valid word'
        else:
            reply = self.reply_for(guess, self.TARGET)
            for c in range(self.nC):
                self.CELL[(c,self.G_NBR)].style = {'button_color': self.COLOR[reply[c]]}
                if reply[c] == '.':
                    self.KEY[guess[c]].style = {'button_color': 'gray'}
            
            if reply == 5*'G':
                self.MESSAGE.disabled = False
                self.MESSAGE.description = f'You win! Agent guessed: {self.solve_wordle()}. Press this button to play again'
            else:
                if self.G_NBR == 5:
                    self.MESSAGE.disabled = False
                    self.MESSAGE.description = f'No more guesses left. Agent guessed {self.solve_wordle()}. Press this button to play again'
                else:
                    self.C_NBR = 0
                    self.G_NBR += 1

    def get_message(self):
        layout = widgets.Layout(width='auto', height='50px') #set width and height

        button = widgets.Button(description='Select enter after each guess.',
                                disabled=True, display='flex', flex_flow='column', 
                                align_items='stretch',layout = layout)
        button.on_click(self.new_game)
        return button

    def new_game(self, b):
        self.TARGET = choice(self.WORDS)
        self.C_NBR, self.G_NBR = 0, 0
        for cell in self.CELL:
            self.CELL[cell].description = ' '
            self.CELL[cell].style = {'button_color': 'white'}
        for ltr in self.LTRS:
            self.KEY[ltr].style = {'button_color': 'white'}
        self.MESSAGE.description = 'Select enter after each guess.'
        self.MESSAGE.disabled = True
    
    def play_game(self):
        display(self.BOARD)
        display(self.MESSAGE)
        display(self.KEYBOARD)

    def get_tree(self):
        with urlopen('https://raw.githubusercontent.com/SumitraMukherjee/wordle/main/successor.txt') as json_file:
            data = json.load(json_file)
        S = dict((int(k), v) for k,v in data.items())
        with urlopen('https://raw.githubusercontent.com/SumitraMukherjee/wordle/main/guess.txt') as json_file:
            data = json.load(json_file)
        G = dict((int(k), v) for k,v in data.items())
        return S, G

    def solve_wordle(self):
        res = []
        node = 0
        guess = self.G[node]
        reply = self.reply_for(guess, self.TARGET)
        res.append(guess)
        while reply != 5*'G':
            node = self.S[node][reply]
            guess = self.G[node]
            reply = self.reply_for(guess, self.TARGET)
            res.append(guess)
        return ', '.join(res)
