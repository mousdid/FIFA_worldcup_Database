import mysql.connector
from sql_function_help import (
    read_table_data,
    get_col_names,
    update_row,
    delete_row,
    set_safe_updates,
    get_row,
)
from query_help_functions import (
    choose_table,
    request_attributes,
    obtain_values,
    get_pk_id,
)
import time
import initialize_db
import deliv5fcns as df
import pandas as pd

database_name = "cs425_fifa_fa24"           # Database name

setup_file = "cs425_fifa_fa24_db_setup.sql" # Default setup file name
db_setup_path = f"deliverable4/cs425_fifa_fa24_db_setup.sql" # Default setup file path

default_host = "localhost"              # set default host name here
default_user = "root"                   # set default user name here
default_password = "QWERTY1234@"       # set default password name here 

commit = True  # variable that determines if sql functions are commmited

tables = [
    "game",
    "game_players",
    "player",
    "stadium",
    "team",
    "team_game",
    "team_products",
    "tv_channel",
    "tv_channel_game",
]

choices = [
    "Create Record",
    "Read Data",
    "Update Record",
    "Delete Record",
    "Custom Query",
    "Access Our Custom Stats"
]

#def prompt_user():
    

"""use_default = input("Would you like to use default options? (y/n) ")

if use_default.lower() != "y":
    host = input("Enter the MySQL host (e.g., 'localhost'): ")
    user = input("Enter your MySQL username: ")
    password = input("Enter your MySQL password: ")
else:
    host = default_host
    user = default_user
    password = default_password"""

host = default_host
user = default_user
password = default_password

def create_new_db(host, user, password):
    global db_setup_path
    global setup_file
    create_db = input(f"Create '{database_name}' Database? (y/n) ")
    if create_db.lower() == "y":
        path = input(
            f"\nIs {db_setup_path} the correct path to the file {setup_file} or the setup file?\nIf yes, leave blank. Otherwise enter the correct file path: "
        )
    else:
        path = ""

    if path not in [" ", ""]:
        db_setup_path = path

    if create_db.lower() == "y":
        create_db = input(
            f"This will delete any previous '{database_name}' database available.\nAre you sure you want to create '{database_name}' Database? (y/n) "
        )
        if create_db.lower() == "y":

            print("Creating Database...")
            try:
                initialize_db.run_sql_script_from_file(
                    db_setup_path, host, user, password
                )
            except OSError as e:
                print(e)
                print("\nError: Could not find the file specified. Try changing the path.\n")
            except:
                print("\nError: Unable to connect to MySQL. \n")


def old_main(cursor):
    """Main function to run the program. This prompts the user for their options from the variable list 'choices'."""

    # Initial loop
    while True:

        print("\nAvailable Options:")

        # prints their available options along with their key
        for i in range(len(choices)):
            print(f"{i+1}. {choices[i]}")

        print("\nEnter 'Exit' or Nothing to Exit")
        print("Enter 'Back' to go back")
        choice = input("Enter Your Choice: ")
        print("")

        # checks if choice variable is an available option of if the user wants to exit
        if choice not in "1234560" and choice.lower() not in ["exit", ""]:
            print("Incorrect Input\n")
            continue

        if choice.lower() in ["exit", ""]:  # checks for exit
            break

        elif int(choice) == 1:  # Choice 1 Create Record
            table_choice = choose_table(tables)

            if table_choice.lower() == "back":
                continue

            if table_choice.lower() in ["", "exit"]:
                break

            write_data(tables[int(table_choice) - 1], insert=True)

        elif int(choice) == 2:  # Choice 2 Read Data

            table_choice = choose_table(tables)

            if table_choice.lower() == "back":
                continue

            if table_choice.lower() in ["", "exit"]:
                break

            table_name = tables[int(table_choice) - 1]

            read_table(table_name)

        elif int(choice) == 3:
            table_choice = choose_table(tables)

            if table_choice.lower() == "back":
                continue

            if table_choice.lower() in ["", "exit"]:
                break

            table_choice = tables[int(table_choice) - 1]

            write_data(table_choice, insert=False)

            pass

        elif int(choice) == 4:
            table_choice = choose_table(tables)

            if table_choice.lower() == "back":
                continue

            if table_choice.lower() in ["", "exit"]:
                break

            table_choice = tables[int(table_choice) - 1]

            delete_data(table_choice)

        elif int(choice) == 5:  # Choice 5 Custom Query
            query = input("Enter Custom Query or Enter 'Back' to go back: ")

            run_new_query(query)

        elif int(choice) == 6: 
            df.access_custom_stats(cursor)  # Call the function from deliv5fcns
        
        elif int(choice) == 0:
            drop_database(database_name)


def read_table(table, cursor):
    """Presents a table to the user based on the input variable table.

    Args:
        table (string): table which user wants to view
    """

    """col_df = (display_cols_types(table, cursor))
    print(col_df.to_string(index=False))"""

    # Read data from the table
    select_query = read_table_data(table)

    try:
        cursor.execute(select_query)
    except mysql.connector.errors.ProgrammingError: 
        raise SyntaxError("Query is not Functional.")
    table_data = cursor.fetchall()

    cols = [description[0] for description in cursor.description]


    dataframe = pd.DataFrame(table_data, columns=cols)
    return dataframe


def delete_data(table, cursor, connection):
    """Deletes a row from the specified table

    Args:
        table (string): name of table the user wants to delete row from
    """
    # loop for incorrect inputs
    while True:
        read_table(table)

        pk, pk_id = get_pk_id(table, cursor, delete=True)
        # pk (string): column name(s) for primary key(s)
        # pk (pk_id): specified row(s) by pk the user wants to delete

        if pk_id is None:
            print("Going Back...")
            return

        cursor.reset()
        select_row_query = get_row(
            table, pk, pk_id
        )  # query which selects the specified row

        cursor.execute(select_row_query)
        row = cursor.fetchall()

        if not row:
            print("\nInvalid Selection\n")
            continue

        print("\nRow Selected for Deletion:")
        print(row)
        # confirms the user wants to delete specified row
        confirmation = input(
            "\nAre you sure this is the row you want deleted? (y/n) "
        )

        if "y" not in confirmation.lower():
            continue

        cursor.reset()
        query = delete_row(table, pk, pk_id)  # deletes row

        print("Deleting Row", end="")
        time.sleep(0.5)
        print(".", end="")
        time.sleep(0.5)
        print(".", end="")
        time.sleep(0.5)
        print(".")
        time.sleep(0.5)

        set_safe_updates(cursor, safe_updates=False)

        try:
            cursor.execute(query)
            read_table(table)
        except (
            mysql.connector.errors.ProgrammingError
        ) as error:  # SQL Syntax error
            print(f"\n{error}\nError on Deletion - Please re-enter ID(s).")
            continue
        except mysql.connector.errors.IntegrityError as error:
            print(  # SQL Foreign Key error
                f"\nForeign Key Error - Rows cannot be deleted from table as other tables are dependent on them."
            )
            continue

        set_safe_updates(cursor, safe_updates=True)

        if commit:
            connection.commit()

        print("\nRow Deleted!")

        return


def run_new_query(query, cursor):
    """Allows the user to create a custom query. Only for development purposes currently

    Args:
        query (string): string of query the user wants to do
    """
    if query.lower() == "pass" or query.lower() == "back":
        return
    
    try:
        cursor.execute(query)
    except:
        print("Error - Please re-enter query")
    query_data = cursor.fetchall()
    for row in query_data:
        print(row)


def write_data(table, cursor, connection, insert=True):
    """Writes data to a given table either through an insert or an update.

    Args:
        table (string): table name being written to
        insert (bool, optional): determines if data is being updated or inserted. Defaults to True.
    """
    # insert row
    if insert:
        # cols - list of all the columns in the table
        # attribute_values - list of the appropriate indexes of the columns wanting to be written to
        cols, attribute_values = request_attributes(
            table, cursor=cursor, insert=True
        )

        # checks if user wants to go back
        if not attribute_values:
            return

        # creates attr_string which is the selected columns seperated by commas surrounded with parenthesis
        attr_string = cols[0]
        for i in range(1, len(cols)):
            attr_string = attr_string + ", " + cols[i]

        while True:  # Loop for errors inserting into table

            # string based on the values the user wants to write to
            # NULL values for the other columns
            value_str = obtain_values(
                table, cols, attribute_values, insert=insert
            )

            # checks if user wants to go back
            if not value_str:
                return

            try:

                # Query to insert data
                insert_query = (
                    f"INSERT INTO {table} ({attr_string}) VALUES ({value_str});"
                )

                print("Inserting Values", end="")
                time.sleep(0.5)
                print(".", end="")
                time.sleep(0.5)
                print(".", end="")
                time.sleep(0.5)
                print(".")

                # TODO: Returns lots of errors right now. Must complete this and remove the SQL errors its giving.
                try:
                    cursor.execute(insert_query)
                    read_table(table)
                except:
                    print("Error on Insertion - Please try again")
                    continue
                

                if commit:
                    connection.commit()

                return

            except (
                mysql.connector.errors.ProgrammingError
            ) as error:  # SQL Syntax error
                print(
                    f"{error}\nError on Insertion - Please re-enter the data."
                )

    # Update Row
    else:
        # cols - list of all the columns in the table
        # attribute_values - list of the appropriate indexes of the columns wanting to be written to
        cols, attribute_values = request_attributes(
            table, cursor=cursor, insert=False
        )

        # checks if user wants to go back
        if not attribute_values:
            return

        read_table(table)
        pk, pk_id = get_pk_id(table, cursor)

        if not pk:
            return

        while True:

            value_list = obtain_values(
                table, cols, attribute_values, insert=insert
            )

            # creates string assigning values to columns ex: column1 = value1, column2 = value2...
            value_str = ""
            for i in range(len(attribute_values)):
                try:
                    value = int(value_list[i])
                except:
                    value = '"' + value_list[i] + '"'
                value_str = value_str + (
                    cols[attribute_values[i] - 1] + " = " + str(value)
                )
                if i < len(attribute_values) - 1:
                    value_str = value_str + ", "

            cursor.reset()
            query = update_row(table, pk, pk_id, value_str)

            print("Updating Values", end="")
            time.sleep(0.5)
            print(".", end="")
            time.sleep(0.5)
            print(".", end="")
            time.sleep(0.5)
            print(".")
            time.sleep(0.5)

            set_safe_updates(cursor, safe_updates=False)

            try:
                cursor.execute(query)
                read_table(table)
            except (
                mysql.connector.errors.ProgrammingError
            ) as error:  # SQL Syntax error
                print(f"{error}\nError on Update - Please re-enter ID(s).")
                continue

            set_safe_updates(cursor, safe_updates=True)

            if commit:
                connection.commit()

            print("\nUpdated!")

            return
        
def drop_database(db_name, cursor, connection):
            to_drop = input(f"Do you want to drop database {db_name}? (y/n) ") 
            if to_drop.lower() == "y":
                to_drop = input(f"This is final and cannot be undone. Are you sure you want to drop database {db_name}? (y/n) ")
                if to_drop.lower() == "y":
                    set_safe_updates(cursor, safe_updates= False)
                    query = f"DROP DATABASE {db_name}"
                    cursor.execute(query)
                    connection.commit()
                    set_safe_updates(cursor, safe_updates= False)
