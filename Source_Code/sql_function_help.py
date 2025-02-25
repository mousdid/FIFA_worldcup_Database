def read_table_data(table):
    """gives SQL which returns all rows of a table

    Args:
        table (string): specified table name

    Returns:
        string: SQL command which returns all rows of a table
    """
    return f"SELECT * FROM {table};"


def get_col_names(table):
    """Gives SQL command which returns all columns of a table

    Args:
        table (string): specified table name

    Returns:
        string: SQL command which returns all columns of a table
    """
    return f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' AND TABLE_SCHEMA = 'fifa' ORDER BY ORDINAL_POSITION;"


def get_table_descriptions(table):
    """Gives SQL command to obtain the description of a specified table.
        Used to determine primary key attribute(s).

    Args:
        table (string): specified table name

    Returns:
        string: SQL command to obtain the description of a specified table
    """
    return f"DESCRIBE {table}"


def get_row(table, pk, pk_id):
    """Gives SQL command which returns a specified row.

    Args:
        table (string): specified table name
        pk (string(s) list): primary key column name(s) of specified table
        pk_id (int(s) list): selected primary key(s) from user

    Returns:
        string: SQL command which returns a specified row.
    """
    if len(pk) == 1:
        return f"SELECT * FROM {table} WHERE {pk[0]} = {pk_id[0]}"
    else:
        ret = f"SELECT * FROM {table} WHERE "
        for i in range(
            len(pk)
        ):  # if there are more than one primary key, this changes the SQL command for it
            ret = ret + f"{pk[i]} = {pk_id[i]}"
            if i < len(pk) - 1:
                ret = ret + " AND "
        return ret


def update_row(table, pk, pk_id, value_str):
    """Gives SQL command which updates a row to the specified values.

    Args:
        table (string): specified table name
        pk (string(s) list): primary key column name(s) of specified table
        pk_id (int(s) list): selected primary key(s) from user
        value_str (string): string assigning values to columns ex: column1 = value1, column2 = value2...

    Returns:
        string: SQL command which updates a row to the specified values.
    """
    if len(pk) == 1:
        return f"UPDATE {table} SET {value_str} WHERE {pk[0]} = {pk_id[0]};"
    else:
        ret = f"UPDATE {table} SET {value_str} WHERE "
        for i in range(
            len(pk)
        ):  # if there are more than one primary key, this changes the SQL command for it
            ret = ret + f"{pk[i]} = {pk_id[i]}"
            if i < len(pk) - 1:
                ret = ret + " AND "
        return ret


def delete_row(table, pk, pk_id):
    """Gives SQL command which deletes a specified row

    Args:
        table (string): specified table name
        pk (string(s) list): primary key column name(s) of specified table
        pk_id (int(s) list): selected primary key(s) from user

    Returns:
        string: SQL command which deletes a specified row
    """
    if len(pk) == 1:
        return f"DELETE FROM {table} WHERE {pk[0]} = {pk_id[0]};"
    else:
        ret = f"DELETE FROM {table} WHERE "
        for i in range(
            len(pk)
        ):  # if there are more than one primary key, this changes the SQL command for it
            ret = ret + f"{pk[i]} = {pk_id[i]}"
            if i < len(pk) - 1:
                ret = ret + " AND "
        return ret


def set_safe_updates(cursor, safe_updates=True):
    """Sets safe updates to True or false as specified

    Args:
        cursor (cursor): object to perform SQL commands
        safe_updates (bool, optional): Variable which sets safe updates to True or False. Defaults to True.
    """
    query = f"SET SQL_SAFE_UPDATES = {int(safe_updates)};"
    cursor.execute(query)



from datetime import date

def calculate_player_age(birthdate):
    """Calculate the age of a player."""
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


def get_team_total_goals(cursor, team_id):
    """Calculate the total goals scored by a team."""
    query = """
    SELECT SUM(goals) AS total_goals
    FROM Game_Players gp
    JOIN Player p ON gp.player_id = p.player_id
    WHERE p.team_id = %s;
    """
    cursor.execute(query, (team_id,))
    result = cursor.fetchone()
    return result[0] if result and result[0] is not None else 0

def get_stadium_capacity(cursor, stadium_id):
    """Retrieve the capacity of a stadium."""
    query = """
    SELECT capacity
    FROM Stadium
    WHERE stadium_id = %s;
    """
    cursor.execute(query, (stadium_id,))
    result = cursor.fetchone()
    return result[0] if result and result[0] is not None else 0

def get_game_weather_status(cursor, game_id):
    """Retrieve the weather status of a game."""
    query = """
    SELECT weather
    FROM Game
    WHERE game_id = %s;
    """
    cursor.execute(query, (game_id,))
    result = cursor.fetchone()
    return result[0] if result and result[0] is not None else "Unknown"

def get_team_product_price(cursor, team_id, product_id):
    """Retrieve the price of a team product."""
    query = """
    SELECT price
    FROM Team_Products
    WHERE team_id = %s AND product_id = %s;
    """
    cursor.execute(query, (team_id, product_id))
    result = cursor.fetchone()
    return result[0] if result and result[0] is not None else 0.00

    

def validate_formation(formation):
    """Validate if a team formation is valid."""
    try:
        parts = list(map(int, formation.split('-')))
        return sum(parts) == 10
    except ValueError:
        return False
