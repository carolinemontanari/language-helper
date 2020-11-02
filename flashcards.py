import arabic_reshaper
import pandas as pd
import numpy as np
import json
from logging import critical, error, info, warning, debug
import datetime, random, os, csv
import xlrd
import sqlite3


def format_df(excelfile, excelsheet):

    excelfile = excelfile  # path
    sheetname = excelsheet  # tab name
    df = pd.read_excel(excelfile, sheet_name=sheetname)
    # Fix Arabic Columns
    cleaned_arabic_word = reverse_arabic(df["Arabic"])
    cleaned_arabic_sentence = reverse_arabic(df["Sample_Sentence"])
    df.insert(1, "Arabic_Def", cleaned_arabic_word)
    df["Sample_Sentence"] = cleaned_arabic_sentence
    # Clean up English Text
    df["English_Def"] = df["English_Def"].str.lower().str.strip()
    # limiting to columns wanted
    df = df[
        ["Arabic_Def", "Tense", "English_Def", "Date_Added", "Sample_Sentence", "Root"]
    ]

    return df


def reverse_arabic(backwards_column):

    cleaned_arabic = []
    for item in backwards_column:
        if item is not None:
            item = str(item)
            reshaped_text = arabic_reshaper.reshape(item)
            reversed_text = reshaped_text[::-1]
            cleaned_arabic.append(reversed_text)

    return cleaned_arabic


def df_to_sql(df, table_name, db_name):

    db_conn = sqlite3.connect(db_name)
    # cursor to interacte with sql db
    c = db_conn.cursor()
    # getting rid of existing table if exists
    c.execute(
        f"""
	DROP TABLE if exists {table_name};
	
	"""
    )
    # Creating table
    c.execute(
        f"""
		CREATE TABLE {table_name} (
			Arabic_Def TEXT NOT NULL, 
			English_Def TEXT, 
			Tense TEXT,
			Date_Added DATE,
			Sample_Sentence TEXT,
			Root TEXT	
			);
		"""
    )
    df.to_sql(table_name, db_conn, if_exists="append", index=False)
    db_conn.close()

    return None


def get_current_db(table_name, db_name):

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

    return arabic_dict, english_dict, details_dict


def card_game(arabic_dict, english_dict, details_dict):
    terms = details_dict
    menu = None
    while menu != "6":
        print(
            """

	   	ARABIC STUDY ASSISTANT!

	    1 - List Words and Definitions
	    2 - Find Arabic Translation
	    4 - Arabic to English Game
	    6 - Exit

	    """
        )
        menu = input("\t\t\tEnter Menu option: ")
        if menu == "1":  # List Terms
            print("\n")
            list_terms(terms)
            input("\n\tPress 'Enter' to return to Main Menu.\n")
        elif menu == "2":  # Find Term
            details = find_def(english_dict, terms)
        elif menu == "3":  # Add Term
            add_word()
        elif menu == "4":  # Work on Arabic to English
            flash_cards(terms, "Arabic_Def", "English_Def")
        elif menu == "5":  # Work on English to Arabic
            flash_cards(terms, "English_Def", "Arabic_Def")
        elif menu == "6":
            exit()

    return None


def add_word(terms):
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
    print("\n\t\tType 'Exit' to return to Menu\n")
    term = generate_question(terms, direction)
    guess = None
    details = None
    while True:
        guess = input("\tWhat is the translation? ").strip().lower()
        if guess == "show":
            print(term[answer])
            term = generate_question(terms, direction)
        if guess == "help":
            details = help(term)
            for item in details:
                print("\t", item, " : ", details[item], "\n")
            term = term
        if guess == term[answer]:
            print("Correct!")
            if input("\tAnother word?(yes/no)") in ["y", "yes"]:
                term = generate_question(terms, direction)
            else:
                break
        if guess in ["no", "n", "exit"]:
            break

    return None


def generate_question(terms, version):
    term = random.choice(terms)
    print("\n\t", term[version], "\n")

    return term


def list_terms(terms):
    for term in terms:
        print(
            "\n\t", terms[term]["English_Def"], " : ", terms[term]["Arabic_Def"], "\n"
        )

    return None


def help(term):
    exclude_keys = ["Arabic_Def", "English_Def"]
    details = {k: term[k] for k in set(list(term.keys())) - set(exclude_keys)}

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
            print("\n\t", key, " : ", terms[wid][key], "\n")
    else:
        print("\n\tDetails Not Found! \n")

    return details


def main():
    table_name = "arabic"
    database_name = "arabic_fc.db"
    excel_file = ""
    excel_tab = ""
    # df = format_df(excel_file, excel_tab)
    # df_to_sql(df, table_name, database_name)
    data, column_names = get_current_db(table_name, database_name)
    arabic, english, details = create_dicts(data, column_names)
    card_game(arabic, english, details)


if __name__ == "__main__":
    main()
