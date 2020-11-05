from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import arabic_reshaper
import pandas as pd
import os
import sqlite3


def reverse_arabic(backwards_word):
    """ take unformatted arabic word and reformats the text, then reverses correctly"""
    if backwards_word is not None:
        item = str(backwards_word)
        reshaped_text = arabic_reshaper.reshape(item)
        reversed_text = reshaped_text[::-1]
        cleaned_arabic = reversed_text

    return cleaned_arabic


def format_excel(excelfile, excelsheet):
    """ if the data source is excel, then format"""
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


def df_to_sql(df, table_name, db_name):
    """ takes df to sqlite table"""
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
    df.to_sql(table_name, db_conn, if_exists="append", index=False)
    db_conn.close()

    return None


def dict_to_sql(dict_name, table_name, db_name):
    """ takes dictionary to sql """
    db_conn = sqlite3.connect(db_name)
    # cursor to interacte with sql db
    c = db_conn.cursor()
    # getting rid of existing table if exists
    c.execute(
        f"""
    DROP TABLE if exists {table_name};

    """
    )
    if table_name == "arabic_dict":
        c.execute(
            f"""CREATE TABLE  {table_name}(
            A_Arabic TEXT,
            English_Def TEXT,
            Tense TEXT,
            Date_Added TEXT,
            A_Sample_Sentence TEXT DEFAULT NULL,
            A_Root TEXT DEFAULT NULL);
            """
        )
        # Creating table

    if table_name == "numbers":

        c.execute(
            f"""CREATE TABLE IF NOT EXISTS {table_name}(
            Number TEXT,
            A_Standard TEXT,
            A_Lebanese TEXT,
            Arabic_Number TEXT DEFAULT NULL);
            """
        )
        # Creating table

        # Creating table

    for rows in dict_name.values():
        column_values = list(rows.values())
        print(column_values)
        # breakpoint()
        column_lst = list(rows.keys())
        column_names = ", ".join(map(str, column_lst))
        # column_items =', '.join(map(str,column_values))
        place_holder = "?, " * len(column_lst)
        place_holder = place_holder[:-2]
        place_holder = str(place_holder)
        c.executemany(
            f"""INSERT INTO {table_name}({column_names}) VALUES({place_holder}) ;""",
            [column_values],
        )

    db_conn.commit()
    # ne
    # df.to_sql(table_name, db_conn, if_exists="append", index=False)
    db_conn.close()

    return None


def google_sheets(SCOPES, documentid, rangeid):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)
    # breakpoint()

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=documentid, range=rangeid).execute()
    values = result.get("values", [])
    columns = values[0]
    rows = values[1::]
    pos = 0

    for column in columns:
        if column.startswith("A_"):
            for row in rows:
                print(row, pos)
                # print(row[pos])

                if len(row) > pos:
                    row[pos] = reverse_arabic(row[pos])
        else:
            for row in rows:
                row[pos] = row[pos].lower().strip()
                # print(row[pos])
        pos = pos + 1
    # breakpoint()
    return columns, rows
