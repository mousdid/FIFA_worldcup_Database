# deliv5fcns.py

import tkinter as tk
from tkinter import simpledialog
import pandas as pd
import mysql.connector  # Import to handle MySQL errors

def access_custom_stats_handle(stat_choice, frame, cursor, show_frame, frames, access_custom_stats):
    """
    Execute the custom stat based on the user's choice.
    Returns a dataframe that can be displayed in dispay_df. 

    :param stat_choice: The user's choice of stat.
    :param frame: The Tkinter frame where results will be displayed.
    :param cursor: The MySQL cursor object.
    :param show_frame: Function to switch frames in the main GUI.
    :param frames: Dictionary of frames from the main GUI.
    :param access_custom_stats: Function to reset the stats menu.
    """
    try:
        # Clear the frame for displaying results
        for widget in frame.winfo_children():
            widget.destroy()
        
        # Display a heading
        tk.Label(frame, text="Custom Stat Results:", font=("Arial", 16)).pack(pady=10)
        
        # Process the stat_choice
        if stat_choice == "1": # TOP N SCORING PLAYERS
            N = simpledialog.askinteger("Input", "Enter the number of top players to display:", parent=frame)
            if N is not None:
                query = f"""
                WITH PlayerGoals AS (
                    SELECT 
                        P.player_id,
                        P.player_name,
                        SUM(GP.goals) AS total_goals
                    FROM Player P
                    JOIN Game_Players GP ON P.player_id = GP.player_id
                    GROUP BY P.player_id, P.player_name
                ),
                RankedPlayers AS (
                    SELECT
                        player_id,
                        player_name,
                        total_goals,
                        RANK() OVER (ORDER BY total_goals DESC) AS ranked
                    FROM PlayerGoals
                )
                SELECT
                    player_id,
                    player_name,
                    total_goals,
                    ranked
                FROM RankedPlayers
                WHERE ranked <= %s
                ORDER BY ranked;
                """
                try:
                    cursor.execute(query, (N,))
                    results = cursor.fetchall()
                    if results:
                        # Create a DataFrame
                        df = pd.DataFrame(results, columns=["player_id", "player_name", "total_goals", "rank"])
                        # Display the DataFrame in the frame
                        return df

                    else:
                        tk.Label(frame, text="No data found.", font=("Arial", 10)).pack(pady=10)
                except mysql.connector.Error as err:
                    raise err
            else:
                tk.Label(frame, text="No input provided.", font=("Arial", 10)).pack(pady=10)

        elif stat_choice == "2": # Players Without Any Yellow or Red Cards
            query = """
            SELECT player_id, player_name
            FROM Player
            WHERE player_id NOT IN (
                SELECT player_id
                FROM Game_Players
                WHERE yellow_cards > 0 OR red_cards > 0
            );
            """
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    df = pd.DataFrame(results, columns=["player_id", "player_name"])
                    return(df)

                else:
                    tk.Label(frame, text="No data found.", font=("Arial", 10)).pack(pady=10)
            except mysql.connector.Error as err:
                raise err
        
        elif stat_choice == "3": # Players Who Played All Games for Their Team
            query = """
            WITH TeamGames AS (
                SELECT team_id, COUNT(DISTINCT game_id) as total_games
                FROM Team_Game
                GROUP BY team_id
            ),
            PlayerGames AS (
                SELECT P.player_id, P.player_name, P.team_id, COUNT(DISTINCT GP.game_id) as games_played
                FROM Player P
                JOIN Game_Players GP ON P.player_id = GP.player_id
                GROUP BY P.player_id, P.player_name, P.team_id
            )
            SELECT
                P.player_id,
                P.player_name,
                P.team_id
            FROM PlayerGames P
            JOIN TeamGames T ON P.team_id = T.team_id
            WHERE P.games_played = T.total_games;
            """
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    df = pd.DataFrame(results, columns=["player_id", "player_name", "team_id"])
                    return df
                else:
                    tk.Label(frame, text="No data found.", font=("Arial", 10)).pack(pady=10)
            except mysql.connector.Error as err:
                raise err
        
        elif stat_choice == "4": # Average Minutes Played Per Game by Player
            player_name = simpledialog.askstring("Input", "Enter the player's name (or leave blank for all players):", parent=frame)
            if player_name is not None:
                if player_name.strip() == '':
                    query = """
                    WITH PlayerGameTime AS (
                        SELECT
                            player_id,
                            TIME_TO_SEC(TIMEDIFF(end_time, start_time)) / 60 as minutes_played
                        FROM Game_Players
                    )
                    SELECT
                        P.player_id,
                        P.player_name,
                        AVG(PGT.minutes_played) as avg_minutes_played
                    FROM Player P
                    JOIN PlayerGameTime PGT ON P.player_id = PGT.player_id
                    GROUP BY P.player_id, P.player_name;
                    """
                    try:
                        cursor.execute(query)
                        results = cursor.fetchall()
                        if results:
                            df = pd.DataFrame(results, columns=["player_id", "player_name", "avg_minutes_played"])
                            return df
                        else:
                            tk.Label(frame, text="No data found.", font=("Arial", 10)).pack(pady=10)
                    except mysql.connector.Error as err:
                        raise err
                    
                else:
                    query = """
                    WITH PlayerGameTime AS (
                        SELECT
                            player_id,
                            TIME_TO_SEC(TIMEDIFF(end_time, start_time)) / 60 as minutes_played
                        FROM Game_Players
                    )
                    SELECT
                        P.player_id,
                        P.player_name,
                        AVG(PGT.minutes_played) as avg_minutes_played
                    FROM Player P
                    JOIN PlayerGameTime PGT ON P.player_id = PGT.player_id
                    WHERE P.player_name = %s
                    GROUP BY P.player_id, P.player_name;
                    """
                    try:
                        cursor.execute(query, (player_name,))
                        results = cursor.fetchall()
                        if results:
                            df = pd.DataFrame(results, columns=["player_id", "player_name", "avg_minutes_played"])
                            return df
                        else:
                            tk.Label(frame, text="No data found for the specified player.", font=("Arial", 10)).pack(pady=10)
                    except mysql.connector.Error as err:
                        raise err
            else:
                tk.Label(frame, text="No input provided.", font=("Arial", 10)).pack(pady=10)

        elif stat_choice == "5": # Average Attendance by Game Type
            query = """
            SELECT
                game_type,
                AVG(attendance) as avg_attendance
            FROM Game
            GROUP BY game_type
            ORDER BY avg_attendance DESC;
            """
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    df = pd.DataFrame(results, columns=["game_type", "avg_attendance"])
                    return df
                else:
                    tk.Label(frame, text="No data found.", font=("Arial", 10)).pack(pady=10)
            except mysql.connector.Error as err:
                raise err
        elif stat_choice == "6": # Stadiums that Hosted Both 'Group' and 'Finals' Games
            query = """
            SELECT DISTINCT S.stadium_id, S.stadium_name
            FROM Stadium S
            WHERE EXISTS (
                SELECT 1 FROM Game G1 WHERE G1.stadium_id = S.stadium_id AND G1.game_type = 'Group'
            )
            AND EXISTS (
                SELECT 1 FROM Game G2 WHERE G2.stadium_id = S.stadium_id AND G2.game_type = 'Finals'
            );
            """
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    df = pd.DataFrame(results, columns=["stadium_id", "stadium_name"])
                    return df
                else:
                    tk.Label(frame, text="No stadiums hosted both 'Group' and 'Finals' games.", font=("Arial", 10)).pack(pady=10)
            except mysql.connector.Error as err:
                raise err
        elif stat_choice == "7": # Total Goals by Team (with Subtotals using ROLLUP)
            query = """
            SELECT
                T.team_name,
                SUM(GP.goals) as total_goals
            FROM Team T
            JOIN Player P ON T.team_id = P.team_id
            JOIN Game_Players GP ON P.player_id = GP.player_id
            GROUP BY T.team_name WITH ROLLUP
            ORDER BY total_goals DESC;
            """
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    df = pd.DataFrame(results, columns=["team_name", "total_goals"])
                    return df
                else:
                    tk.Label(frame, text="No data found.", font=("Arial", 10)).pack(pady=10)
            except mysql.connector.Error as err:
                raise err
            
        elif stat_choice == "8": # Average Attendance by Weather Condition and Game Type (using CUBE)
            query = """
            SELECT
                COALESCE(weather, 'All Weathers') as weather,
                COALESCE(game_type, 'All Game Types') as game_type,
                AVG(attendance) as avg_attendance
            FROM Game
            GROUP BY weather, game_type WITH ROLLUP
            HAVING weather IS NOT NULL OR game_type IS NOT NULL
            ORDER BY weather, game_type;
            """
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    df = pd.DataFrame(results, columns=["weather", "game_type", "avg_attendance"])
                    return df
                else:
                    tk.Label(frame, text="No data found.", font=("Arial", 10)).pack(pady=10)
            except mysql.connector.Error as err:
                raise err
        elif stat_choice == "9": # Players Who Scored a Goal and Received a Yellow Card
            query = """
            SELECT DISTINCT P.player_id, P.player_name
            FROM Player P
            JOIN Game_Players GP ON P.player_id = GP.player_id
            WHERE GP.goals > 0

            INTERSECT

            SELECT DISTINCT P.player_id, P.player_name
            FROM Player P
            JOIN Game_Players GP ON P.player_id = GP.player_id
            WHERE GP.yellow_cards > 0;
            """
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    df = pd.DataFrame(results, columns=["player_id", "player_name"])
                    return df
                else:
                    tk.Label(frame, text="No players found who have both scored goals and received yellow cards.", font=("Arial", 10)).pack(pady=10)
            except mysql.connector.Error as err:
                raise err

        else:
            tk.Label(frame, text="Invalid Choice. Please select a valid option.", font=("Arial", 10)).pack(pady=10)
        
        # Back button to return to the custom stats menu
        tk.Button(frame, text="Back to Stats Menu", command=access_custom_stats).pack(pady=10)
        # Back to Main Menu
        tk.Button(frame, text="Back to Main Menu", command=lambda: show_frame(frames["main_menu"])).pack(pady=10)
    except Exception as e:
        raise e  # Re-raise the exception to be caught in the calling function
