import arabic_reshaper
import pandas as pd
import numpy as np
import sys
import json
import ipdb
from logging import critical, error, info, warning, debug
import pickle, datetime, random, os, csv
import xlrd
import sqlite3


def format_df():
    df = pd.read_excel("Arabic_Lessons.xlsx", sheet_name="Full_Set")

    # breakpoint()

    # df.index= df.index.str.encode('utf-8')
    cleaned_arabic_word = reverse_arabic(df["Arabic"])
    cleaned_arabic_sentence = reverse_arabic(df["Sample_Sentence"])
    df.insert(1, "Arabic_Def", cleaned_arabic_word)
    df["Sample_Sentence"] = cleaned_arabic_sentence
    df["English_Def"] = df["English_Def"].str.lower()
    # drop misformatted Arabic
    # df = df.drop(columns=["Arabic"])
    df = df[
        ["Arabic_Def", "Tense", "English_Def", "Date_Added", "Sample_Sentence", "Root"]
    ]
    print(df)
    return df


def reverse_arabic(backwards_column):
    cleaned_arabic = []
    for item in backwards_column:
        if item is not None:
            # ipdb.set_trace()
            item = str(item)
            reshaped_text = arabic_reshaper.reshape(item)
            reversed_text = reshaped_text[::-1]
            cleaned_arabic.append(reversed_text)
    return cleaned_arabic


def df_to_sql(df):

    db_conn = sqlite3.connect("arabic_fc.db")
    # # cursor to interacte with sql db
    c = db_conn.cursor()
    c.execute(
        """
		DROP TABLE if exists Arabic;
		
		"""
    )
    c.execute(
        """
	DROP TABLE if exists arabic;
	
	"""
    )
    # Creating table

    c.execute(
        """
		CREATE TABLE arabic (
			Arabic_Def TEXT NOT NULL, 
			English_Def TEXT, 
			Tense TEXT,
			Date_Added DATE,
			Sample_Sentence TEXT,
			Root TEXT	
			);
		"""
    )
    sqlite_table = "arabic"
    df.to_sql(sqlite_table, db_conn, if_exists="append", index=False)
    db_conn.close()

    return sqlite_table


def get_current_db(json_str=False):
    db_conn = sqlite3.connect("arabic_fc.db")
    c = db_conn.cursor()
    column_name = []
    db_conn.row_factory = (
        sqlite3  # This enables column access by name: row['column_name']
    )
    rows = c.execute(
        """
		SELECT rowid, * FROM arabic; 
		"""
    ).fetchall()
    column_details = c.execute(
        """
		PRAGMA table_info(arabic);
		"""
    ).fetchall()
    for item in column_details:
        column_name.append(item[1])
    db_conn.commit()
    db_conn.close()

    return rows, column_name


def create_dicts(rows, columns):
    arabic_dict = {}
    english_dict = {}
    details_dict = {}
    for row in rows:
        strid = row[0]
        arabic_dict[row[1]] = strid
        english_dict[row[2]] = strid
        # ipdb.set_trace()
        inner_dict = dict(zip(columns, row[1::]))
        details_dict[strid] = inner_dict

    print(details_dict)

    return arabic_dict, english_dict, details_dict


def card_game(arabic_dict, english_dict, details_dict):
    terms = details_dict
    print(terms)

    menu = None
    while menu != "6":
        print(
            """

	   	STUDY HELPER!

	    1 - List Words and Definitions
	    2 - Find Arabic Translation
	    3 - Add Term
	    4 - Arabic to English Game
	    5 - English to Arabic Game
	    6 - Exit

	    """
        )
        menu = input("\t\t\tEnter Menu option: ")
        if menu == "1":  # List Terms
            print("\n")
            for term in terms:
                print(term, " : ",terms[term])
            input("\n\tPress 'Enter' to return to Main Menu.\n")
        elif menu == "2":  # Find Term
            details = find_def(english_dict, terms)
            print("\t",details)
        elif menu == "3":  # Add Term
            add_word()
        elif menu == "4":  # Work on Arabic to English
            flash_cards(terms, "Arabic_Def", "English_Def")
        elif menu == "5":  # Work on English to Arabic
            flash_cards(terms, "English_Def", "Arabic_Def")
        elif menu == "6":
            exit()


def add_word(terms):
    term = input("\n\tEnter the new term: ").lower()
    if term not in terms:
        definition = input("\tWhat is the definition? ").lower
        terms[term] = definition
        print("\n\t" + term, "has been added.")
    else:
        print("\n\tThat term already exists!")
        input("\n\tPress 'Enter' to return to Main Menu.\n")


def flash_cards(terms, direction, answer):
    print("\n\t\tType 'Exit' to return to Menu\n")
    term = generate_question(terms, direction)
    guess = None
    details = None
    while guess != "exit":
        guess = input("\tWhat is the translation? ").strip().lower()
        if guess == "show":
            print(term[answer])
            term = generate_question(terms, direction)
        if guess == "help":
            details= help(term)
            for item in details:  
                print("\t",item," : ",details[item],"\n")
            term = term 
        if guess == term[answer]:
            print("Correct!")
            if input("\tAnother word?") in ["y", "yes"]:
                term = generate_question(terms, direction)

    return guess


def generate_question(terms, version):
    term = random.choice(terms)
    print("\n\t",term[version],"\n")
    return term


def help(term):
    exclude_keys =['Arabic_Def', 'English_Def']
    details={k: term[k] for k in set(list(term.keys())) - set(exclude_keys)}
    return details


def find_def(language_Dict, terms):
    word_to_find = input("\t Type word you're looking for and press enter: ")
    lookup = word_to_find.strip()
    str1 = " "
    details = "Details Not Found"
    if lookup in language_Dict.keys():
        wid = language_Dict[lookup]
        details = []
        for key in terms[wid]:
            details.append(str(key) + " : " + str(terms[wid][key]))

    # print("\tWord not Found!")

    return details


# print '\nYour score is:', score
def parse_arguments():
    """Read arguments from a command line."""
    parser = argparse.ArgumentParser(description="Arguments get parsed via --commands")
    parser.add_argument(
        "-v",
        metavar="verbosity",
        type=int,
        default=2,
        help="Verbosity of logging: 0 -critical, 1- error, 2 -warning, 3 -info, 4 -debug",
    )

    args = parser.parse_args()
    verbose = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    logging.basicConfig(format="%(message)s", level=verbose[args.v], stream=sys.stdout)

    return args


def main():
    # df = format_df()
    # breakpoint()
    # table = df_to_sql(df)
    # json_table = get_current_db(json_str = True)
    table, columns = get_current_db()
    arabic, english, details = create_dicts(table, columns)
    # dict_of_terms =retro_dictify(df_of_terms)
    card_game(arabic, english, details)


if __name__ == "__main__":
    # args= parse_arguments()
    main()