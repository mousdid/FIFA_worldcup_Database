import tkinter as tk
from tkinter import messagebox
import pandas as pd
import mysql.connector
import initialize_db
import time
import old_main as om
from tkinter import simpledialog
import modern_sql as ms
import deliv5fcns as d5f

# Placeholder for default file path
default_file_path = "deliverable5/cs425_fifa_fa24_db_setup.sql"
cursor = None
connection = None
# Global variables for frames and defaults
frames = {}
current_defaults = {"host": "localhost", 
                    "user": "root", 
                    "password": "password"}

actions = ['create','read','update','delete','custom','stats']

quitBool = False
dots = 0

def show_frame(frame):
    """ Shows given frame

    Args:
        frame (tk.Frame): Frame object to switch to.
    """
    for f in frames.values():
        f.pack_forget()
    
    frame.pack(fill="both", expand=True)
    
    if frame == frames['connecting']:
        connecting_label = frames['connecting'].connecting_label  # Get the label from the connecting frame
        start_connecting_animation(connecting_label, count = 3)
        
def use_defaults():
    """Use the current default values."""
    print(f"Using Defaults: Host={current_defaults['host']}, User={current_defaults['user']}, Password={current_defaults['password']}")
    show_frame(frames["create_db"])

def save_defaults():
    """Save new default values."""
    global current_defaults
    host = host_entry.get()
    user = user_entry.get()
    password = password_entry.get()
    if host and user:
        current_defaults["host"] = host
        current_defaults["user"] = user
        current_defaults["password"] = password
        messagebox.showinfo("Success","Using new credentials.")
        show_frame(frames["create_db"])
    else:
        messagebox.showerror("Error", "Please fill in all fields.")
        
def create_database():
    """Creates database from the create database frame.
    """
    file_path = file_path_entry.get()
    if not file_path:
        file_path = default_file_path
    if messagebox.askyesno("Confirmation", f"Are you sure you want to create a database using {file_path}?\nAny database titled cs425_fifa_fa24 will be replaced."):
        try:
            initialize_db.run_sql_script_from_file(
                    file_path, current_defaults['host'],current_defaults['user'],current_defaults['password']
            )
            messagebox.showinfo("Success", f"Database created successfully using: {file_path}")
        except OSError as e:
            messagebox.showerror("Error","Could not find the file specified. Try changing the path.")
            create_database()
            return
        except:
            messagebox.showerror("Error","Unable to connect to MySQL.")
            create_database()
            return

        show_frame(frames["connecting"])
            
def start_connecting_animation(connecting_label, count = 3):
    """Start the 'Connecting...' animation."""
    global dots
    dots = (dots + 1) % 4  # Cycle through 0, 1, 2, 3
    connecting_label.config(text="Connecting" + "." * dots)  # Update the label text
    if count > 0:
        frames["connecting"].after(1000, lambda: start_connecting_animation(connecting_label, count - 1))
    else: 
        stop_connecting_animation(connecting_label)
        connect_to_db(current_defaults['host'], current_defaults["user"], current_defaults["password"])

def stop_connecting_animation(connecting_label):
    """Stop the 'Connecting...' animation."""
    connecting_label.config(text="Connected!")

def table_action(action):
    """Perform the selected action for a specific table."""
    def perform_action(table_name):
        if action == actions[0]:    # Create Record
            insert_record(table_name, frames["insert_frame"], om.read_table(table_name,cursor))
        elif action == actions[1]:    # Read table
            display_df(frames["table_frame"], om.read_table(table_name,cursor))
        elif action == actions[2]:    # Update Record
            display_df_update(frames["table_frame"], om.read_table(table_name,cursor), table_name)
        elif action == actions[3]:    # Delete Record
            display_df_delete(frames["table_frame"], om.read_table(table_name,cursor), table_name)
        
        
    # Clear and populate the table action frame
    for widget in frames["table_action"].winfo_children():
        widget.destroy()

    tk.Label(frames["table_action"], text=f"Select a table for {action}", font=("Arial", 14)).pack(pady=10)
    tables = [
        "game", "game_players", "player", "stadium", "team",
        "team_game", "team_products", "tv_channel", "tv_channel_game"
    ]

    for table in tables:
        tk.Button(frames["table_action"], text=table, width=30,
                  command=lambda t=table: perform_action(t)).pack(pady=5)

    tk.Button(frames["table_action"], text="Back", command=lambda: show_frame(frames["main_menu"])).pack(pady=10)
    show_frame(frames["table_action"])

def access_custom_stats():
    """
    Handles the 'Access Our Custom Stats' option in the GUI.
    Displays a list of custom stats as buttons for the user to select.
    """
    # Clear and populate the custom_stats frame
    frame = frames["custom_stats"]
    for widget in frame.winfo_children():
        widget.destroy()
    
    tk.Label(frame, text="Accessing Custom Stats:", font=("Arial", 16)).pack(pady=10)
    tk.Label(frame, text="Please choose one of the following stats:", font=("Arial", 12)).pack(pady=5)
    
    stats = [
        ("Top N Scoring Players", "1"),
        ("Players Without Any Yellow or Red Cards", "2"),
        ("Players Who Played All Games for Their Team", "3"),
        ("Average Minutes Played Per Game by Player", "4"),
        ("Average Attendance by Game Type", "5"),
        ("Stadiums that Hosted Both 'Group' and 'Finals' Games", "6"),
        ("Total Goals by Team (with Subtotals using ROLLUP)", "7"),
        ("Average Attendance by Weather Condition and Game Type (using CUBE)", "8"),
        ("Players Who Scored a Goal and Received a Yellow Card","9")
    ]
    
    def handle_stat_choice(stat_value):
        try:
           df= d5f.access_custom_stats_handle(
                stat_value,
                frame,
                cursor,
                show_frame,
                frames,
                access_custom_stats  # Pass the function itself
            )
           display_df(frame,df)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            # Optionally, navigate back to the stats menu
            access_custom_stats()
    
    for stat_text, stat_value in stats:
        tk.Button(
            frame,
            text=stat_text,
            font=("Arial", 10),
            width=60,
            command=lambda sv=stat_value: handle_stat_choice(sv)
        ).pack(pady=2)
    
    # Back button to return to the main menu
    tk.Button(frame, text="Back to Main Menu", command=lambda: show_frame(frames["main_menu"])).pack(pady=10)
    
    # Show the custom_stats frame
    show_frame(frame)


def start_gui():
    """Initialize and start the GUI."""
    global frames, host_entry, user_entry, password_entry, file_path_entry

    # Initialize Tkinter application
    root = tk.Tk()
    root.title("FIFA Database Manager")

    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = 800
    window_height = 600
    
    x_coordinate = int((screen_width/2) - (window_width/2))
    y_coordinate = int((screen_height/2) - (window_height/2))
    root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")



    # Bind the Escape key to exit windowed fullscreen
    root.bind("<Escape>", lambda event: root.overrideredirect(False))

    # Create a container frame for the main content
    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    # Create a frame for the quit button at the bottom
    quit_frame = tk.Frame(root)
    quit_frame.pack(side="bottom", fill="x")

    # Add the Quit button to the quit_frame
    quit_button = tk.Button(quit_frame, text="Quit", command=root.destroy)
    quit_button.pack(pady=10)

    # Defaults Frame
    frames["defaults"] = tk.Frame(container)
    tk.Label(frames["defaults"], text="MySQL Login Credentials", font=("Arial", 16)).pack(pady=10)

    tk.Label(frames["defaults"], text="Current Default Credentials:", font=("Arial", 12)).pack(pady=5)
    tk.Label(frames["defaults"], text=f"Host: {current_defaults['host']}").pack()
    tk.Label(frames["defaults"], text=f"User: {current_defaults['user']}").pack()
    tk.Label(frames["defaults"], text=f"Password: {current_defaults['password']}").pack()

    tk.Label(frames["defaults"], text="New Host:").pack(pady=5)
    host_entry = tk.Entry(frames["defaults"], width=40)
    host_entry.pack(pady=5)
    tk.Label(frames["defaults"], text="New User:").pack(pady=5)
    user_entry = tk.Entry(frames["defaults"], width=40)
    user_entry.pack(pady=5)
    tk.Label(frames["defaults"], text="New Password:").pack(pady=5)
    password_entry = tk.Entry(frames["defaults"], show="*", width=40)
    password_entry.pack(pady=5)

    tk.Button(frames["defaults"], text="Use Default Credentials", command=use_defaults).pack(pady=5)
    tk.Button(frames["defaults"], text="Proceed with new credentials", command=save_defaults).pack(pady=10)

    # Create Database Frame
    frames["create_db"] = tk.Frame(container)
    tk.Label(frames["create_db"], text="Create New Database?", font=("Arial", 16)).pack(pady=10)
    tk.Label(frames["create_db"], text=f"Current File Path: {default_file_path}", font=("Arial", 12)).pack(pady=10)
    tk.Label(frames["create_db"], text="Specify a new file path (optional):").pack(pady=5)
    file_path_entry = tk.Entry(frames["create_db"], width=40)
    file_path_entry.pack(pady=5)
    tk.Button(frames["create_db"], text="Create Database", command=create_database).pack(pady=10)
    tk.Button(frames["create_db"], text="Skip Database Creation", command=lambda: show_frame(frames["connecting"])).pack(pady=10)

    # Connecting Frame
    frames["connecting"] = tk.Frame(container)
    connecting_label = tk.Label(frames["connecting"], text="Connecting to database", font=("Arial", 16))
    connecting_label.pack(pady=20)
    frames["connecting"].connecting_label = connecting_label

    # Operations Menu Frame
    frames["main_menu"] = tk.Frame(container)
    tk.Label(frames["main_menu"], text="Main Menu", font=("Arial", 14)).pack(pady=10)
    tk.Button(frames["main_menu"], text="Create Record", command=lambda: table_action(actions[0]), width=30).pack(pady=5)
    tk.Button(frames["main_menu"], text="Read Data", command=lambda: table_action(actions[1]), width=30).pack(pady=5)
    tk.Button(frames["main_menu"], text="Update Record", command=lambda: table_action(actions[2]), width=30).pack(pady=5)
    tk.Button(frames["main_menu"], text="Delete Record", command=lambda: table_action(actions[3]), width=30).pack(pady=5)
    tk.Button(frames["main_menu"], text="Custom Query", command=lambda: custom_query(), width=30).pack(pady=5)
    tk.Button(frames["main_menu"], text="Access Custom Stats", command=lambda:access_custom_stats(), width=30).pack(pady=5)
    tk.Button(frames["main_menu"], text="Back to Credentials", command=lambda: show_frame(frames["defaults"])).pack(pady=5)

    # Table Action Frame
    frames["table_action"] = tk.Frame(container)

    # Read table
    frames["table_frame"] = tk.Frame(container)

    # Insert Frame
    frames["insert_frame"] = tk.Frame(container)

    #custom stats
    frames["custom_stats"] = tk.Frame(container)

    # Custom Query
    frames["custom_query"] = tk.Frame(container)

    # Start at Defaults Frame
    show_frame(frames["defaults"])

    # Run the Tkinter event loop
    root.mainloop()

def connect_to_db(host = current_defaults['host'], user = current_defaults['user'], password = current_defaults["password"], database_name =  "cs425_fifa_fa24"):
    global connection, cursor
    try:
        # Connect to the MySQL server
        connection = mysql.connector.connect(
            host=host, user=user, password=password, database=database_name
        )

        if connection.is_connected():
            show_frame(frames["main_menu"])
            # Create a cursor object to interact with the database
            cursor = connection.cursor()


    except mysql.connector.Error as error:
        messagebox.showerror("Error","Unable to connect to MySQL Server. Try changing credentials. ")
        show_frame(frames["defaults"])
    finally:
        if connection:
            if connection.is_connected() and quitBool:
                cursor.close()
                connection.close()
                print("MySQL connection is closed")
                print("Goodbye.")

def display_df(frame, df):
    """
    Display a pandas DataFrame in a Tkinter frame, showing 10 rows at a time.
    :param frame: The Tkinter frame where the DataFrame should be displayed.
    :param df: The pandas DataFrame to display.
    """
    # Pagination variables
    show_frame(frame)
    rows_per_page = 10
    cols_per_page = 6
    current_row_page = tk.IntVar(value=0)
    current_col_page = tk.IntVar(value=0)

    def update_table():
        """Update the table to show the current row and column page."""
        for widget in frame.winfo_children():
            widget.destroy()  # Clear the frame

        # Centering
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(rows_per_page + 3, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        # Calculate row and column ranges
        start_row = current_row_page.get() * rows_per_page
        end_row = start_row + rows_per_page
        start_col = current_col_page.get() * cols_per_page
        end_col = start_col + cols_per_page

        subset = df.iloc[start_row:end_row, start_col:end_col]  # Get the current page

        # Create a container frame for the table
        table_container = tk.Frame(frame)
        table_container.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)

        # Display column headers
        for col_index, col_name in enumerate(subset.columns):
            tk.Label(table_container, text=col_name, font=("Arial", 12, "bold"),
                     borderwidth=2, relief="solid", width=15).grid(row=0, column=col_index)

        # Display rows
        for row_index, row in enumerate(subset.itertuples(index=False), start=1):
            for col_index, cell in enumerate(row):
                tk.Label(table_container, text=cell, font=("Arial", 10), borderwidth=1,
                         relief="solid", width=15).grid(row=row_index, column=col_index)

        # Row navigation buttons
        tk.Button(frame, text="↑\nPrevious Rows", command=lambda: change_page(-1, 0),
                  state=tk.NORMAL if current_row_page.get() > 0 else tk.DISABLED).grid(
            row=0, column=1, sticky="s")

        tk.Button(frame, text="Next Rows\n↓", command=lambda: change_page(1, 0),
                  state=tk.NORMAL if end_row < len(df) else tk.DISABLED).grid(
            row=rows_per_page + 2, column=1, sticky="s")

        # Column navigation buttons
        tk.Button(frame, text="← Previous Columns", command=lambda: change_page(0, -1),
                  state=tk.NORMAL if current_col_page.get() > 0 else tk.DISABLED).grid(
            row=1, column=0, sticky="e")

        tk.Button(frame, text="Next Columns →", command=lambda: change_page(0, 1),
                  state=tk.NORMAL if end_col < len(df.columns) else tk.DISABLED).grid(
            row=1, column=2, sticky="w")

        # Page info
        tk.Label(frame, text=f"Rows: Page {current_row_page.get() + 1} of {len(df) // rows_per_page + 1}",
                 font=("Arial", 10)).grid(row=rows_per_page + 3, column=0, sticky="w")
        tk.Label(frame, text=f"Cols: Page {current_col_page.get() + 1} of {len(df.columns) // cols_per_page + 1}",
                 font=("Arial", 10)).grid(row=rows_per_page + 3, column=2, sticky="e")

        tk.Button(frame, text="Main Menu", command=lambda: show_frame(frames["main_menu"])).grid(
            row=rows_per_page + 3, column=1, pady=10)

    def change_page(row_offset, col_offset):
        """Change the current row or column page and update the table."""
        current_row_page.set(current_row_page.get() + row_offset)
        current_col_page.set(current_col_page.get() + col_offset)
        update_table()

    update_table()

def display_df_update(frame, df, table_name):
    """
    Display a pandas DataFrame in a Tkinter frame, showing 10 rows at a time.
    :param frame: The Tkinter frame where the DataFrame should be displayed.
    :param df: The pandas DataFrame to display.
    """
    # Pagination variables
    show_frame(frame)
    rows_per_page = 10
    cols_per_page = 6
    current_row_page = tk.IntVar(value=0)
    current_col_page = tk.IntVar(value=0)

    # Variables to keep track of selected row and columns
    selected_row = tk.IntVar(value=-1)  # Initialize with -1 to indicate no selection

    selected_columns_vars = {}  # Key: column name, Value: BooleanVar

    def update_table():
        """Update the table to show the current row and column page."""
        nonlocal selected_columns_vars
        for widget in frame.winfo_children():
            widget.destroy()  # Clear the frame

        # Centering
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(rows_per_page + 4, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(cols_per_page + 2, weight=1)

        # Calculate row and column ranges
        start_row = current_row_page.get() * rows_per_page
        end_row = min(start_row + rows_per_page, len(df))
        start_col = current_col_page.get() * cols_per_page
        end_col = min(start_col + cols_per_page, len(df.columns))

        subset = df.iloc[start_row:end_row, start_col:end_col]  # Get the current page
        displayed_columns = subset.columns.tolist()

        # Create a container frame for the table
        table_container = tk.Frame(frame)
        table_container.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)

        # Display column headers with checkboxes
        for col_index, col_name in enumerate(displayed_columns):
            # Use existing BooleanVar or create a new one
            if col_name not in selected_columns_vars:
                selected_columns_vars[col_name] = tk.BooleanVar(value=True)
            col_var = selected_columns_vars[col_name]

            # Checkbox for column selection
            cb = tk.Checkbutton(table_container, variable=col_var)
            cb.grid(row=0, column=col_index + 1, sticky='nsew')

            # Column header label
            tk.Label(table_container, text=col_name, font=("Arial", 12, "bold"),
                     borderwidth=2, relief="solid", width=15).grid(row=1, column=col_index + 1)

        # Reset selected_row when the page changes
        # Ensure that one row is always selected by defaulting to the first row on the current page
        if subset.index.tolist():
            selected_row.set(subset.index[0])
        else:
            selected_row.set(-1)  # No rows to select

        # Display rows with radio buttons
        for row_display_index, (idx, row) in enumerate(subset.iterrows(), start=2):
            # Radio button for row selection
            rb = tk.Radiobutton(table_container, variable=selected_row, value=idx)
            rb.grid(row=row_display_index, column=0, padx=5)
            # Display each cell in the row
            for col_index, cell in enumerate(row):
                tk.Label(table_container, text=cell, font=("Arial", 10), borderwidth=1,
                         relief="solid", width=15).grid(row=row_display_index, column=col_index + 1)

        # Row navigation buttons
        tk.Button(frame, text="↑\nPrevious Rows", command=lambda: change_page(-1, 0),
                  state=tk.NORMAL if current_row_page.get() > 0 else tk.DISABLED).grid(
            row=0, column=1, sticky="s")

        tk.Button(frame, text="Next Rows\n↓", command=lambda: change_page(1, 0),
                  state=tk.NORMAL if end_row < len(df) else tk.DISABLED).grid(
            row=rows_per_page + 3, column=1, sticky="s")

        # Column navigation buttons
        tk.Button(frame, text="← Previous Columns", command=lambda: change_page(0, -1),
                  state=tk.NORMAL if current_col_page.get() > 0 else tk.DISABLED).grid(
            row=1, column=0, sticky="e")

        tk.Button(frame, text="Next Columns→", command=lambda: change_page(0, 1),
                  state=tk.NORMAL if end_col < len(df.columns) else tk.DISABLED).grid(
            row=1, column=cols_per_page + 2, sticky="w")

        # Page info
        total_row_pages = ((len(df) - 1) // rows_per_page) + 1
        total_col_pages = ((len(df.columns) - 1) // cols_per_page) + 1

        tk.Label(frame, text=f"Rows: Page {current_row_page.get() + 1} of {total_row_pages}",
                 font=("Arial", 10)).grid(row=rows_per_page + 4, column=0, sticky="w")
        tk.Label(frame, text=f"Cols: Page {current_col_page.get() + 1} of {total_col_pages}",
                 font=("Arial", 10)).grid(row=rows_per_page + 4, column=cols_per_page + 2, sticky="e")

        # Update Selected Rows and Columns Button
        tk.Button(frame, text="Update Selected Rows and Columns", command=update_selected).grid(
            row=rows_per_page + 4, column=1, pady=10)

        tk.Button(frame, text="Main Menu", command=lambda: show_frame(frames["main_menu"])).grid(
            row=rows_per_page + 5, column=1, pady=10)

    def change_page(row_offset, col_offset):
        """Change the current row or column page and update the table."""
        current_row_page.set(current_row_page.get() + row_offset)
        current_col_page.set(current_col_page.get() + col_offset)
        update_table()

    def update_selected():
        """Handle the update of selected rows and columns."""
        # Get the selected row index
        selected_row_index = selected_row.get()
        if selected_row_index == -1:
            messagebox.showwarning("No Selection", "Please select a row to update.")
            return

        # Get the selected columns
        selected_cols = [col for col, var in selected_columns_vars.items() if var.get()]
        if not selected_cols:
            messagebox.showwarning("No Selection", "Please select at least one column to update.")
            return

        # Proceed to update the selected row and columns
        # Open a new frame to collect new values
        open_update_frame(selected_row_index, selected_cols)

    def open_update_frame(row_index, columns):
        """Open a new frame to input new values for selected columns."""
        # Create a new Toplevel window
        update_window = tk.Toplevel()
        update_window.title("Update Row")

        # Center the window
        window_width = 400
        window_height = 50 + 30 * (len(columns)+2)
        screen_width = update_window.winfo_screenwidth()
        screen_height = update_window.winfo_screenheight()
        x_coordinate = int((screen_width/2) - (window_width/2))
        y_coordinate = int((screen_height/2) - (window_height/2))
        update_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Create a container frame
        container = tk.Frame(update_window)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        entry_vars = {}  # To hold StringVars for entries

        # Display each selected column with an entry field
        for idx, col in enumerate(columns):
            tk.Label(container, text=col, font=("Arial", 12)).grid(row=idx, column=0, sticky="e", pady=5)
            var = tk.StringVar()
            entry = tk.Entry(container, textvariable=var, width=30)
            entry.grid(row=idx, column=1, pady=5)
            entry_vars[col] = var

        # Submit button
        def submit_updates():
            new_values = {col: var.get() for col, var in entry_vars.items() if var.get()}
            updated_values = [new_values.get(col, None) for col in df.columns]  # List of updated values or None
            try:
                ms.update_table(table_name,df.loc[row_index], updated_values, cursor, connection, commit = True)
            except ValueError:
                messagebox.showerror("Update Error", "Unable to Update. Perhaps Foreign Key Error?\nPlease Try again.")
                update_window.destroy()
                return

            if new_values:
                # Update the DataFrame
                for col, val in new_values.items():
                    df.at[row_index, col] = val

                messagebox.showinfo("Success", "Row updated successfully.")
                update_window.destroy()
                update_table()  # Refresh the table to show updated values
            else:
                messagebox.showwarning("No Input", "Please enter new values.")

        tk.Button(container, text="Submit", command=submit_updates).grid(row=len(columns), column=0, columnspan=2, pady=10)

    update_table()

def display_df_delete(frame, df, table_name):
    """
    Display a pandas DataFrame in a Tkinter frame, showing 10 rows at a time, with an option to delete rows.
    :param frame: The Tkinter frame where the DataFrame should be displayed.
    :param df: The pandas DataFrame to display.
    """
    # Pagination variables
    show_frame(frame)

    for widget in frame.winfo_children():
        widget.destroy()
        
    rows_per_page = 10
    cols_per_page = 6
    current_row_page = tk.IntVar(value=0)
    current_col_page = tk.IntVar(value=0)

    

    # Variables to keep track of selected row    
    selected_row = tk.IntVar(value=-1)  # Initialize with -1 to indicate no selection
    tk.Button(frame, text="Main Menu", command=lambda: show_frame(frames["main_menu"])).pack(pady=5)

    def update_table():
        """Update the table to show the current row and column page."""
        for widget in frame.winfo_children():
            widget.destroy()  # Clear the frame

        # Centering
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(rows_per_page + 4, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(cols_per_page + 2, weight=1)

        # Calculate row and column ranges
        start_row = current_row_page.get() * rows_per_page
        end_row = min(start_row + rows_per_page, len(df))
        start_col = current_col_page.get() * cols_per_page
        end_col = min(start_col + cols_per_page, len(df.columns))

        subset = df.iloc[start_row:end_row, start_col:end_col]  # Get the current page
        displayed_columns = subset.columns.tolist()

        # Create a container frame for the table
        table_container = tk.Frame(frame)
        table_container.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)

        # Display column headers
        for col_index, col_name in enumerate(displayed_columns):
            tk.Label(table_container, text=col_name, font=("Arial", 12, "bold"),
                     borderwidth=2, relief="solid", width=15).grid(row=0, column=col_index + 1)

        # Reset selected_row when the page changes
        # Ensure that one row is always selected by defaulting to the first row on the current page
        if subset.index.tolist():
            selected_row.set(subset.index[0])
        else:
            selected_row.set(-1)  # No rows to select

        # Display rows with radio buttons
        for row_display_index, (idx, row) in enumerate(subset.iterrows(), start=2):
            # Radio button for row selection
            rb = tk.Radiobutton(table_container, variable=selected_row, value=idx)
            rb.grid(row=row_display_index, column=0, padx=5)
            # Display each cell in the row
            for col_index, cell in enumerate(row):
                tk.Label(table_container, text=cell, font=("Arial", 10), borderwidth=1,
                         relief="solid", width=15).grid(row=row_display_index, column=col_index + 1)

        # Row navigation buttons
        tk.Button(frame, text="↑\nPrevious Rows", command=lambda: change_page(-1, 0),
                  state=tk.NORMAL if current_row_page.get() > 0 else tk.DISABLED).grid(
            row=0, column=1, sticky="s")

        tk.Button(frame, text="Next Rows\n↓", command=lambda: change_page(1, 0),
                  state=tk.NORMAL if end_row < len(df) else tk.DISABLED).grid(
            row=rows_per_page + 3, column=1, sticky="s")

        # Column navigation buttons
        tk.Button(frame, text="← Previous Columns", command=lambda: change_page(0, -1),
                  state=tk.NORMAL if current_col_page.get() > 0 else tk.DISABLED).grid(
            row=1, column=0, sticky="e")

        tk.Button(frame, text="Next Columns→", command=lambda: change_page(0, 1),
                  state=tk.NORMAL if end_col < len(df.columns) else tk.DISABLED).grid(
            row=1, column=cols_per_page + 2, sticky="w")

        # Page info
        total_row_pages = ((len(df) - 1) // rows_per_page) + 1
        total_col_pages = ((len(df.columns) - 1) // cols_per_page) + 1

        tk.Label(frame, text=f"Rows: Page {current_row_page.get() + 1} of {total_row_pages}",
                 font=("Arial", 10)).grid(row=rows_per_page + 4, column=0, sticky="w")
        tk.Label(frame, text=f"Cols: Page {current_col_page.get() + 1} of {total_col_pages}",
                 font=("Arial", 10)).grid(row=rows_per_page + 4, column=cols_per_page + 2, sticky="e")

        # Delete Selected Row Button
        tk.Button(frame, text="Delete Selected Row", command=delete_selected).grid(
            row=rows_per_page + 4, column=1, pady=10)

        tk.Button(frame, text="Main Menu", command=lambda: show_frame(frames["main_menu"])).grid(
            row=rows_per_page + 5, column=1, pady=10)

    def change_page(row_offset, col_offset):
        """Change the current row or column page and update the table."""
        current_row_page.set(current_row_page.get() + row_offset)
        current_col_page.set(current_col_page.get() + col_offset)
        update_table()

    def delete_selected():
        """Handle the deletion of the selected row."""
        # Get the selected row index
        selected_row_index = selected_row.get()
        ms.delete_row_from_table(table_name, df.loc[selected_row_index],cursor, connection)

        if selected_row_index == -1:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected row?"):
            return

        # Delete the row from the DataFrame
        df.drop(selected_row_index, inplace=True)
        df.reset_index(drop=True, inplace=True)

        messagebox.showinfo("Success", "Row deleted successfully.")
        update_table()  # Refresh the table to reflect the deleted row

    update_table()

def insert_record(table_name, insert_frame, df):
    show_frame(insert_frame)
    # Clear the frame before displaying new content
    for widget in insert_frame.winfo_children():
        widget.destroy()

    # Set the title label for inserting a record
    title_label = tk.Label(insert_frame, text=f"Insert Record into {table_name}", font=("Arial", 16, "bold"))
    tk.Button(insert_frame, text="Main Menu", command=lambda: show_frame(frames["main_menu"])).pack(pady=5)
    title_label.pack(pady=10)

    # Get columns for the selected table from the dataframe
    columns = df.columns.tolist()

    # Create a container frame for input fields within the provided insert_frame
    container = tk.Frame(insert_frame)
    container.pack(fill="both", expand=True, padx=20, pady=20)
    entry_vars = {}  # To hold StringVars for entries

    # Display each column with an entry field
    for idx, col in enumerate(columns):
        tk.Label(container, text=col, font=("Arial", 12)).grid(row=idx, column=0, sticky="e", pady=5)
        var = tk.StringVar()
        entry = tk.Entry(container, textvariable=var, width=30)
        entry.grid(row=idx, column=1, pady=5)
        entry_vars[col] = var

    # Submit button
    def submit_insert():
        new_values = {col: var.get() for col, var in entry_vars.items() if var.get()}
        if new_values:
            try:
                ms.insert_into_table(table_name, df, new_values, cursor, connection, commit=True)
                messagebox.showinfo("Success", "Record inserted successfully.")
                # Clear the input fields after successful insertion
                for var in entry_vars.values():
                    var.set("")
            except ValueError:
                messagebox.showerror("Insert Error", "Unable to Insert. Please check the values and try again.")
        else:
            messagebox.showwarning("No Input", "Please enter values for the new record.")

    tk.Button(container, text="Submit", command=submit_insert).grid(row=len(columns), column=0, columnspan=2, pady=10)


def custom_query():
    show_frame(frames["custom_query"])
    frame = frames["custom_query"]


    for widget in frame.winfo_children():
        widget.destroy()

    # Label and text box for query input
    query_label = tk.Label(frame, text="Enter your custom SQL query:", font=("Arial", 12))
    query_label.pack(pady=10)

    query_text = tk.Text(frame, height=10, width=50)
    query_text.pack(pady=10)

    # Function to run the custom query
    def run_query():
        query = query_text.get("1.0", "end-1c")  # Get query from text box
        if query:
            try:
                result_df = ms.query_to_df(query, cursor, connection, commit = True)
            except:
                messagebox.showerror("Error", f"Query was unable to execute.")
                return
            display_df(frame, result_df)
            messagebox.showinfo("Query Result", f"Query executed successfully.")
                
        else:
            messagebox.showwarning("No Input", "Please enter a SQL query to execute.")

    # Run button
    run_button = tk.Button(frame, text="Run Query", command=run_query)
    run_button.pack(pady=10)




if __name__ == "__main__":
    start_gui()
