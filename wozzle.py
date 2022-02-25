import copy
import datetime
import gzip
import os
import random
import re
import sys
import urllib.request

from typing import List

# a source to use when generating a list of correct words:
# using Simple English Wikipedia
WORDS_SOURCE_URL: str = 'https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-all-titles-in-ns0.gz'

# the directory that this programme is running
EXECUTION_DIRECTORY: str = os.path.dirname(__file__) + '/'

# an intermediate file
INTERMEDIATE_FILE: str = 'intermediate.txt'

# a file of a list of correct words
WORDS_LIST_FILE: str = 'words_list.txt'

# a string to prompt for correct input of string
INCORRECT_VALUE_SENTENCE: str = 'unwanted value: an alphabetic-charactered word with 5 letters required'

# a string for winner
ALL_CORRECT_EMOJIS: str = '✅✅✅✅✅\n 💮   C O N G R A T S   💮 '

# a correct character
CORRECT_CHARACTER: str = '✅'

# a character in different spots
DIFFERENT_SPOTS_CHARACTER: str = '🟨'

# a wrong character
WRONG_CHARACTER: str = '⬛'


def main() -> None:
    if len(sys.argv) >= 2:
        _argument_value = sys.argv[1].lower()

    # exit programme after initialisation of the list when needed
    if len(sys.argv) >= 2 and any([
        _argument_value == '-i',
        _argument_value == '--initialise',
        _argument_value == '--initialize'
    ]):
        init(initialise_requested=True)
        sys.exit()

    else:
        init()

    # exit programme with correct answer when needed
    if len(sys.argv) >= 2:
        if any([
            _argument_value == '-s', _argument_value == '--surrender',
        ]):
            exec(player_surrendered=True)

        elif all([
            len(_argument_value) == 5,
            re.match('^[a-zA-Z]+$', _argument_value),
        ]):
            exec(input_word=_argument_value)

        else:
            print(INCORRECT_VALUE_SENTENCE)

    else:
        print(INCORRECT_VALUE_SENTENCE)


# generate when the list does not exist
def init(initialise_requested: bool = False) -> None:
    # specify a dump file
    _dump_file: str = os.path.basename(WORDS_SOURCE_URL)

    # when the initialisation is requested,
    # or a file of list containing correct words does not found or is empty
    if initialise_requested or not(os.path.isfile(EXECUTION_DIRECTORY + WORDS_LIST_FILE)) or os.path.getsize(EXECUTION_DIRECTORY + WORDS_LIST_FILE) == 0:

        if os.path.isfile(EXECUTION_DIRECTORY + WORDS_LIST_FILE):
            os.remove(EXECUTION_DIRECTORY + WORDS_LIST_FILE)

        # download a latest dump file of Simple English Wikipedia
        urllib.request.urlretrieve(
            WORDS_SOURCE_URL,
            EXECUTION_DIRECTORY + _dump_file,
        )

        # open the dump file and extract the content
        with gzip.open(
            EXECUTION_DIRECTORY + _dump_file,
            mode='rt',
            encoding='utf-8',
        ) as _dump:

            # make an empty intermadiate file
            with open(
                EXECUTION_DIRECTORY + INTERMEDIATE_FILE,
                mode='w',
            ) as _intermediate:

                _content: str = _dump.read()
                _intermediate.write(_content)

        # delete the dump file
        os.remove(EXECUTION_DIRECTORY + _dump_file)

        # make an empty list file for correct words
        with open(
            EXECUTION_DIRECTORY + WORDS_LIST_FILE,
            mode='a',
        ) as _list:

            # reopen the intermediate file
            with open(
                EXECUTION_DIRECTORY + INTERMEDIATE_FILE,
                mode='r',
                encoding='utf-8',
            ) as _intermediate:

                # read each line of the intermediate file
                for _line in _intermediate:

                    # save an alphabetic-charactered word with 5 letters + LF
                    # to the list
                    if len(_line) == 6 and re.match('^[a-zA-Z]+$', _line):
                        _list.write(_line)

        # delete the intermediate file
        os.remove(EXECUTION_DIRECTORY + INTERMEDIATE_FILE)


# define the word of today and examine
def exec(input_word: str = None, player_surrendered: bool = False):
    # fix the seed by the date, then pick a line from the list
    random.seed(int(datetime.date.today().strftime('%Y%m%d')))
    correct_word: str = random.choice(
        open(EXECUTION_DIRECTORY + WORDS_LIST_FILE).readlines()
    ).strip().lower()

    # TODO: somewhere would be better place to code `sys.exit()` than here
    if player_surrendered:
        print(correct_word.upper())
        sys.exit()

    # TODO: somewhere would be better place to code `sys.exit()` than here
    if input_word == correct_word:
        print(ALL_CORRECT_EMOJIS)
        sys.exit()

    # TODO: collation of `input_word` and `correct_word` desired
    else:
        _examinations: List[bool] = [input_word == correct_word for input_word,
                                     correct_word in zip(input_word, correct_word)]
        _correctnesses: List[str] = []
        _scanner: List[str] = []

        for _index, _each in enumerate(_examinations):
            _correctnesses += CORRECT_CHARACTER if _each else correct_word[_index]

        _scanner = copy.deepcopy(_correctnesses)
        _chaser: int = 0

        for _input_index, _input_character in enumerate(input_word):
            if _correctnesses[_input_index] == CORRECT_CHARACTER:
                del _scanner[_input_index - _chaser]
                _chaser += 1
                continue

            _counter: int = _scanner.count(_input_character)
            _dictionary: List[dict] = {}

            if any([_counter == 0, _dictionary.get(_input_character) == 0]):
                _correctnesses[_input_index] = WRONG_CHARACTER
                continue
            elif _input_character not in _dictionary:
                _dictionary[_input_character] = _counter

            _correctnesses[_input_index] = DIFFERENT_SPOTS_CHARACTER
            _dictionary[_input_character] = (_counter - 1)

        print(''.join(_correctnesses))


if __name__ == '__main__':
    main()
