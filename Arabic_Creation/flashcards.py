import random
import sqlite3
from collections import namedtuple
from sql_db_creation import *


class performance:
    date: str
    game: str
    word: str
    correct: bool
    guesses: int


def get_current_db(table_name, db_name):
    """ connect to current database and return contents of specified table"""
    # Connect to db
    db_conn = sqlite3.connect(db_name)
    c = db_conn.cursor()
    column_name = []
    # This enables column access by name: row['column_name']
    db_conn.row_factory = sqlite3
    rows = c.execute(
        f"""
		SELECT rowid, * FROM {table_name}; 
		"""
    ).fetchall()
    # get list of column details
    column_details = c.execute(
        f"""
		PRAGMA table_info({table_name});
		"""
    ).fetchall()
    # limiting to column names
    for item in column_details:
        column_name.append(item[1])
    db_conn.commit()
    db_conn.close()

    return rows, column_name


def num_list(rows):
    """ format number table into necessary small dictionary"""
    english_num = []
    arabic_num = []
    for row in rows:
        english_num.append(int(row[1]))
        arabic_num.append(row[3])
    arabic_num_dict = dict(zip(english_num, arabic_num))

    return arabic_num_dict


def create_dicts(rows, columns):
    """ creating dictionary from dictonary table"""

    arabic_dict = {}
    english_dict = {}
    details_dict = {}
    arabic_column = columns[0]
    english_column = columns[1]

    for row in rows:

        strid = row[0]
        arabic_dict[row[1]] = strid
        english_dict[row[2]] = strid
        inner_dict = dict(zip(columns[0::], row[1::]))
        details_dict[strid] = inner_dict

    return arabic_dict, english_dict, details_dict, arabic_column, english_column


def noindex_create_dicts(rows, columns):
    """ creating dictionary from dictonary table"""
    details_dict = {}
    for row in rows:
        strid = row[0]
        inner_dict = dict(zip(columns[0::], row[0::]))
        details_dict[strid] = inner_dict
    # breakpoint()
    return details_dict


def card_game(
    arabic_dict, english_dict, details_dict, arabic_column, english_column, numbers
):
    """ base section of study assistant printed in console"""
    terms = details_dict
    print(terms)
    menu = None
    while menu != "6":
        print(
            """

	   	ARABIC STUDY ASSISTANT!

	    1 - List Words and Definitions
	    2 - Find Arabic Translation
        3 - Get Numbers
	    4 - Arabic to English Game
	    6 - Exit

	    """
        )
        menu = input("\t\t\tEnter Menu option: ")
        if menu == "1":  # List Terms
            print("\n")
            list_terms(terms, arabic_column, english_column)
            input("\n\tPress 'Enter' to return to Main Menu.\n")
        elif menu == "2":  # Find Term
            details = find_def(english_dict, terms)
        elif menu == "3":  # Add Term
            guess_the_number(numbers)
        elif menu == "4":  # Work on Arabic to English
            flash_cards(terms, arabic_column, english_column)
        elif menu == "5":  # Work on English to Arabic
            flash_cards(terms, english_column, arabic_column)
        elif menu == "6":
            exit()


def add_word(terms):
    """add word to database """
    term = input("\n\tEnter the new term: ").lower()
    if term not in terms:
        definition = input("\tWhat is the definition? ").lower
        terms[term] = definition
        print("\n\t" + term, "has been added.")
    else:
        print("\n\tThat term already exists!")
        input("\n\tPress 'Enter' to return to Main Menu.\n")

    return None


def flash_cards(terms, direction, answer):
    """flash card game"""
    print("\n\t\tType 'Exit' to return to Menu\n")
    term = generate_question(terms, direction)
    guess = None
    details = None
    n = 0
    while True:

        guess = input("\tWhat is the translation? ").strip().lower()
        n = +1
        if guess == "show":
            # performance("",direction, term[answer], 0, n )
            print(term[answer])
            term = generate_question(terms, direction)
        if guess == "help":
            details = help(term, direction, answer)
            for item in details:
                print("\t", item, " : ", details[item], "\n")
            term = term
        if guess == term[answer]:
            print("Correct!")
            # performance("",direction, term[answer], 1, n )
            if input("\tAnother word?(yes/no)") in ["y", "yes"]:
                term = generate_question(terms, direction)
            else:
                break
        if guess in ["no", "n", "exit"]:
            break

    return None


def generate_question(terms, version):
    """ getting random word from dict"""
    term = random.choice(terms)
    print("\n\t", term[version], "\n")

    return term


def list_terms(terms, arabic_column, english_column):
    """ list all terms in dict"""
    for term in terms:
        print(
            "\n\t", terms[term][english_column], " : ", terms[term][arabic_column], "\n"
        )

    return None


def help(term, arabic_column, english_column):
    """ show all details of word"""
    exclude_keys = [arabic_column, english_column]
    details = {k: term[k] for k in set(list(term.keys())) - set(exclude_keys)}

    return details


def find_def(language_Dict, terms):
    """ input word you're looking for and search dict"""
    word_to_find = input("\t Type word you're looking for and press enter: ")
    lookup = word_to_find.strip()
    str1 = " "
    details = "Details Not Found"
    if lookup in language_Dict.keys():
        wid = language_Dict[lookup]
        details = []
        for key in terms[wid]:
            print("\n\t", key, " : ", terms[wid][key], "\n")
    else:
        print("\n\tDetails Not Found! \n")

    return details


def guess_the_number(numbers):
    """inputted number"""
    print("\tEnter 'exit' to return to main menu")
    num = None
    while True:
        num = input("\n\tEnter number: ").strip().replace(",", "")
        if num in ["no", "n", "exit", ""]:
            break
        else:
            try:
                formatted_num = int_ar(numbers, num)
                print(formatted_num)
            except:
                print("not a valid number!")


def int_ar(numbers, num, join=True):
    """get written arabic of inputted number"""
    d = numbers
    k = 1000
    ks = k * 10
    m = k * 1000
    b = m * 1000
    num = int(num)

    if int(str(num)[0]) == 2:
        hundred = d[200]
        thousand = d[2_000]
        thousands = d[10_000]
        millions = d[2_000_000]
    else:
        hundred = d[100]
        thousand = d[1_000]
        thousands = d[10_000]
        millions = d[1_000_000]

    if num < 21:
        arabic = d[num]

    elif num < 100:
        if num % 10 == 0:
            arabic = d[num]
        else:
            arabic = d[num // 10 * 10] + " " + d[num % 10]

    elif num < k:
        if num % 100 == 0:
            arabic = hundred + " " + d[num // 100]
            if hundred == d[200] or int(str(num)[0])==1:
                arabic = hundred 
                
        else:
            next_level = int_ar(numbers, num % 100)
            arabic = next_level + " ؤ " + hundred + " " + d[num // 100]
            if hundred == d[200]or int(str(num)[0])==1:
                arabic = next_level + " ؤ " + hundred

    elif num < ks:
        if num % k == 0:
            next_level = int_ar(numbers, num // k)
            arabic = hundred + " " + next_level
            if thousand == d[2_000] or int(str(num)[0])==1:
                arabic = thousand
        else:
            next_level = int_ar(numbers, num % k)
            last_level = int_ar(numbers, num // k)
            arabic = next_level + " ؤ  " + thousand + " " + last_level
            if thousand == d[2_000] or int(str(num)[0])==1:
                arabic = next_level + " ؤ  " + thousand             

    elif num < m:
        if num % k == 0:
            next_level = int_ar(numbers, num // k)
            arabic = thousands + " " + next_level
        else:
            next_level = int_ar(numbers, num % k)
            last_level = int_ar(numbers, num // k)
            arabic = next_level + " ؤ  " + thousands + " " + last_level
    elif num < b:
        if num % k == 0:
            next_level = int_ar(numbers, num // k)
            arabic = thousands + " " + next_level
        else:
            next_level = int_ar(numbers, num % k)
            last_level = int_ar(numbers, num // k)
            arabic = next_level + " ؤ  " + thousands + " " + last_level

    # raise AssertionError("num is too large: %s" % str(num))

    return arabic


def main():
    dict_table_name = "arabic_dict"
    num_table_name = "numbers"
    database_name = "arabic_fc_b.db"   
    numbers, num_column_names = get_current_db(num_table_name, database_name)
    data, column_names = get_current_db(dict_table_name, database_name)
    num_dict = num_list(numbers)
    # breakpoint()
    arabic, english, details, arabic_column, english_column = create_dicts(
        data, column_names
    )

    # guess_the_number(num_dict)

    card_game(arabic, english, details, arabic_column, english_column, num_dict)


if __name__ == "__main__":
    main()
