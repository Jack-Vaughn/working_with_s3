#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
menu.py
02 Nov 2020
MENU CLASS TAKE TAKES MENU-OPTIONS FOR USER INPUT
"""

__author__ = 'Jack Vaughn'
__license__ = '0BSD'
__version__ = '0.1.0'
__maintainer__ = 'Jack Vaughn'
__email__ = 'jack.vaughn0523@gmail.com'
__status__ = 'Production'


from typing import List
from typing import Dict


class MenuOption:
    """
    MENU OPTION CLASS THAT GOES INSIDE OF MENU CLASS
    """
    def __init__(self, menu_text: str, confirmation_text: str, function: any = lambda: None,
                 exit_option: bool = False, alternatives: List[str] = []):
        self.menu_text = menu_text
        self.confirmation_text = confirmation_text
        self.function = function
        self.exit_option = exit_option
        self.alternatives = alternatives


class Menu:
    """
    MENU CLASS TAKE TAKES MENU-OPTIONS FOR USER INPUT
    """
    def __init__(self, prompt: str, menu_options: Dict[str, MenuOption]):
        self.prompt = prompt
        self.menu_options = menu_options
        self.should_exit = False

    def show_prompt(self) -> None:
        print(self.prompt)

    def show(self) -> None:
        for number, menu_option in self.menu_options.items():
            print(f'    {number}. {menu_option.menu_text}')

    def choose_option(self):
        choice: str = input()
        choice_is_valid = choice in self.menu_options.keys()
        if not choice_is_valid:  # ONLY CHECK THE ALTERNATIVES IF IT ISN'T IN THE KEYS
            for key, value in self.menu_options.items():
                if choice in value.alternatives:
                    choice_is_valid = True
                    choice = key  # IF IT IS AN ALTERNATIVE, CHANGE THE CHOICE TO THE KEY
        if not choice_is_valid:
            print('Invalid choice. Please try again.\n')
            self.choose_option()
            return  # NOT NECESSARY BUT HELPS ME REMEMBER WHAT THE FLOW IS
        else:
            print(self.menu_options[choice].confirmation_text)
            function_return = self.menu_options[choice].function()
            if self.menu_options[choice].exit_option:
                self.should_exit = True
            return function_return
