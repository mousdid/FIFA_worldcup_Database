from sql_function_help import get_col_names, get_table_descriptions, get_row
import pandas as pd


def choose_table(tables):
    """Prompts the user to choose a table for various uses.

    Args:
        tables (string list): list of strings of the possible table names

    Returns:
        string: string that is 1 greater than the table in the table list or string that can be used to exit program or go back.
    """
    print("Tables:")
    for i in range(len(tables)):  # Prints the options for the tables
        print(f"{i+1}. {tables[i]}")

    table_choice = input("\nWhich table do you want to view? ")

    # checks for incorrect choices
    while table_choice not in "123456789" and table_choice.lower() != "back":

        print("Incorrect Input\n")
        table_choice = input("Which table do you want to view? ")

    return table_choice


def request_attributes(table, cursor, insert=True):
    """Prompts the user for attributes(columns) from the table they provided

    Args:
        table (string): table name from which the data will be accessed
        cursor (cursor): value which helps with using sql functions (idk how it works or what it does)

    Returns:
        cols (string list): cols is the names of the columns
        cols_keys (int list): list of 0s and 1s that associate with cols
    """
    cursor.execute(get_col_names(table))
    columns = cursor.fetchall()  # obtains column names

    while True:
        cols = []  # adds the first column to the cols string
        print("\nAttributes:")
        for i in range(
            len(columns)
        ):  # adds the rest of the columns to cols seperated by |
            cols.append(columns[i][0])
            print(f"{i+1}. {cols[i]}")

        attributes = input(
            f"\nSelect Attributes by key that you want to {["update","insert"][insert]}. Separate by spaces or select all by entering '*': "
        )  # the input list of digits

        if (attributes.strip()).lower() in ["exit", ""]:  # checks if user wants to exit
            return None

        # checks if user wants to change all columns
        if attributes in ["*"]:
            attributes = list(range(1, len(cols) + 1))

        else:

            attributes = attributes.strip().split(
                " "
            )  # turns attributes into a list of just numbers
            try:
                attributes = [
                    (int(i)) for i in attributes
                ]  # checks if all items in the list can be ints
            except:
                print("\nNon Numeric Characters entered")
                print("Please re-enter the attribute keys")
                continue

            if any(
                (i > len(cols) + 1) for i in attributes
            ):  # checks if ints have no associated attributes
                print("Please input an available attribute")
                continue

            if 0 in attributes:
                print("Please input a non-zero attribute")
                continue

            if len(attributes) != len(set(attributes)):
                print("Do not enter duplicates")
                continue

        return cols, attributes  # returns the associated column names from the keys


def obtain_values(table, cols, attributes, insert=True):
    """Prompts the user to give values when previously prompted for specific attributes.

    Args:
        table (string): table name from which the data will be inserted/updated
        cols (string list): list of strings of column names
        attributes (int list): list of chosen attributes related to cols
        insert (bool, optional): from the function write_data that determines if data will be updated or inserted. Defaults to True.

    Returns:
        string: the appropriate values for the appropriate columns in order to insert into the table, NULL otherwise
                if insert is set to false it just returns the users input
    """

    attr_names = list(
        cols[i - 1] for i in attributes
    )  # list of column names the user wants to write to


    attr_string = attr_names[0]
    for i in range(
        1, len(attr_names)
    ):  # Creates attr_string which is the chosen columns seperated by commas
        attr_string = attr_string + ", " + attr_names[i]

    values = input(
        f"\nInput data separated by commas to {["update","insert"][insert]} into table '{table}' on columns:\n{attr_string}\n"
    )

    if not values:
        return None

    values = values.split(",")

    for i in range(len(values)):
        values[i] = values[i].strip()
    
    if not insert:  # checks if the user just wants to update columns
        return values  # returns just a list of the stripped values as further string editing has to be done

    # Creates value_str which is string that specifies the values the user wants inserted
    # and NULL for the values they don't want inserted
    value_str = ""
    count = 0
    for i in range(len(cols)):
        if i+1 in attributes:
            try:
                value = int(values[count])
            except:
                value = f'"{values[count]}"'

            value_str = value_str + str(value)
            count += 1
        else:
            value_str = value_str + "NULL"
        if i != len(cols) - 1:
            value_str = value_str + ", "

    return value_str


def get_pkey_attr(table, cursor):
    """Goes through columns of specified table to find which column(s) are the primary key(s)

    Args:
        table (string): specified table name
        cursor (cursor): used for SQL Commands

    Returns:
        string list: list of attribute name(s) of the primary key(s) of the specified table
    """
    cursor.execute(get_table_descriptions(table))
    query_data = cursor.fetchall()

    pks = []
    for row in query_data:
        if row[3] == "PRI":
            pks.append(row[0])

    return pks


def get_pk_id(table, cursor, delete=False):
    """Prompts the User to specify primary key(s) to select a row.

    Args:
        table (string): Specified table name
        cursor (cursor): used for SQL commands
        delete (bool, optional): specifies if data is used for updating or deleting. Defaults to False.

    Returns:
        string list - pk: list of the attributes of the primary key(s)
        integer list - pk_id: list of the specified primary key(s) from the user
    """
    pk = get_pkey_attr(table, cursor)

    while True:
        pk_id = []
        for i in range(len(pk)):
            pk_id.append(
                input(
                    f"\nEnter {pk[i]} of row you wish to {["update","delete"][delete]}: "
                )
            )
            if pk_id[i].lower() in ["exit", "back", "", " "]:
                return None, None
        try:
            cursor.execute(get_row(table, pk, pk_id))
            break
        except:
            print("Invalid ID - Please re-enter")
            continue

    return pk, pk_id


# TODO: Create function that goes through the columns of the table and specifies how they should be based on their datatype


def display_cols_types(table, cursor):
    cursor.execute(get_table_descriptions(table))
    query_data = cursor.fetchall()

    col_df = pd.DataFrame(columns=["column", "type", "can_be_null"])

    for row in query_data:
        null_val = True if row[2] == "YES" else False
        col_df.loc[len(col_df)] = [row[0], row[1], null_val]

    return col_df
