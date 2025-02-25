import mysql.connector
import os



def run_sql_script_from_file(script_file, host, user, password):
    """Function that connects to the SQL server and runs each of the commands in a file.
        This function is currently only used to read commands off the file "cs425_fifa_fa24_db_setup.sql"

    Args:
        script_file (string): path to database setup .sql file
        host (string): host name for the user's MySQL server.
        user (string): user name for the user's MySQL server.
        password (string): password for the user's MySQL server

    """

    global use_default

    os.chmod(script_file, 0o644)
    # Prompt user for connection details

    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(host=host, user=user, password=password)

        cursor = connection.cursor()

        # Open the SQL file and read its content
        with open(script_file, "r") as file:
            sql_script = file.read()

        # Split the script into individual statements based on semicolons
        sql_commands = sql_script.split(";")

        # Execute each command
        for command in sql_commands:
            if command.strip():  # Only execute non-empty commands
                cursor.execute(command)

        # Commit the changes
        connection.commit()
        print("SQL script executed successfully. Database Created!")

    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
