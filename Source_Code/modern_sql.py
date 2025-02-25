from query_help_functions import get_pk_id, obtain_values
from sql_function_help import update_row, set_safe_updates, delete_row, get_col_names
from query_help_functions import request_attributes
import pandas as pd
import old_main as om
import mysql.connector

# Indexes of primary keys per table
table_pk = {'game': [0],
            'game_players': [0,1],
            'player': [0],
            'stadium': [0],
            'team': [0],
            'team_game': [0,1],
            "team_products": [0,1],
            "tv_channel": [0],
            "tv_channel_game":[0,1]}

def query_to_df(query, cursor, connection, commit = False):
    """ Returns a dataframe of the output of a custom query. 

    Args:
        query (string): Custom query input
        cursor (cursor): cursor object for sql commands
        connection (connection): Connection for sql commands
        commit (bool, optional): Commits changes to database. Defaults to False.

    Raises:
        SyntaxError: Raised if query is not functional 

    Returns:
        DataFrame: DataFrame of query output
    """
    
    try:
        cursor.execute(query)
    except mysql.connector.errors.ProgrammingError: 
        raise SyntaxError("Query is not Functional.")
    table_data = cursor.fetchall()

    cols = [description[0] for description in cursor.description]

    df = pd.DataFrame(table_data, columns=cols)

    return df

def update_table(table, row, updates, cursor, connection, commit = False):
    """ Updates given row in given table with given values

    Args:
        table (string): table name
        row (Series): pandas series of the row.
        updates (list): list of updated values. None if not updated
        cursor (cursor): cursor object for sql commands
        connection (connection): Connection for sql commands
        commit (bool, optional): Commits changes to database. Defaults to False.

    Raises:
        ValueError: Raised if Query doesn't work
    """

    # cols - list of all the columns in the table
    # attribute_values - list of the appropriate indexes of the columns wanting to be written to
    #cols = updates
    attribute_values = []
    values = []
    cols = row.index.tolist()

    for i in range(len(updates)):
        if updates[i] is not None:
            attribute_values.append(i)
            values.append(updates[i])


    pk_index = table_pk[table]
    pk = []
    pk_id = []
    for i in pk_index:
        pk.append(cols[i])
        pk_id.append(row[i])
    



    # creates string assigning values to columns ex: column1 = value1, column2 = value2...
    value_str = ""
    for i in range(len(attribute_values)):
        try:
            value = int(values[i])
        except:
            value = '"' + values[i] + '"'
        value_str = value_str + (
            cols[attribute_values[i]] + " = " + str(value)
        )
        if i < len(attribute_values) - 1:
            value_str = value_str + ", "

    #print(value_str)

    cursor.reset()
    query = update_row(table, pk, pk_id, value_str)
    set_safe_updates(cursor, safe_updates=False)

    cursor.execute(query)
    try:
        cursor.execute(query)
    except:
        raise ValueError("Unable to Update")
    
    set_safe_updates(cursor, safe_updates=True)

    if commit:
        connection.commit()

    return

def delete_row_from_table(table, row, cursor, connection, commit = False):
    """ Deletes given row from table. 

    Args:
        table (string): table name
        row (list): list of row to delete
        cursor (cursor): cursor object for sql commands
        connection (connection): Connection for sql commands
        commit (bool, optional): Commits changes to database. Defaults to False.

    Raises:
        ValueError: Rises if query does not work
    """


    cols = row.index.tolist()
    pk_index = table_pk[table]
    pk = []
    pk_id = []
    for i in pk_index:
        pk.append(cols[i])
        pk_id.append(row[i])
    

    cursor.reset()
    query = delete_row(table, pk, pk_id)
    set_safe_updates(cursor, safe_updates=False)

    try:
        cursor.execute(query)
    except:
        raise ValueError("Unable to Update")
    set_safe_updates(cursor, safe_updates=True)

    if commit:
        connection.commit()

    return

def insert_into_table(table, table_df, value_dict, cursor, connection, commit = False):
    """Writes data to a given table either through an insert or an update.

    Args:
        table (string): table name being written to
        insert (bool, optional): determines if data is being updated or inserted. Defaults to True.
    """
    cols = table_df.columns.tolist()


    # creates attr_string which is the selected columns seperated by commas surrounded with parenthesis
    attr_string = cols[0]
    for i in range(1, len(cols)):
        attr_string = attr_string + ", " + cols[i]

    print(cols)
    values = []
    for col in cols:
        values.append(value_dict[col])
    
    value_str = ""
    for i in range(len(values)):
        try:
            value = int(values[i])
        except:
            value = '"' + values[i] + '"'
        value_str = value_str + (str(value))
        if i < len(values) - 1:
            value_str = value_str + ", "
    

    try:

        # Query to insert data
        insert_query = (
            f"INSERT INTO {table} ({attr_string}) VALUES ({value_str});")

        try:
            cursor.execute(insert_query)
        except:
            raise ValueError("Try Again")
        

        if commit:
            connection.commit()

        return

    except:
        raise ValueError("Unable to Insert")
    


