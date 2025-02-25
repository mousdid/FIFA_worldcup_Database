-- MySQL Commands that create the database "cs425_fifa_fa24" and insert mock data into it

SET SQL_SAFE_UPDATES = 0;
drop database if exists cs425_fifa_fa24;
create database if not exists cs425_fifa_fa24;
use cs425_fifa_fa24;
SET SQL_SAFE_UPDATES = 1;

CREATE TABLE Team (
    team_id tinyint PRIMARY KEY AUTO_INCREMENT, -- Unique identifier for each team
    team_name VARCHAR(25),
    group_name CHAR(1),                    -- Group name for the team in the tournament (e.g., Group A)
    coach_name VARCHAR(50),                   -- Name of the coach
    coach_nationality CHAR(3)             -- Nationality of the coach
);

-- Create Stadium table
CREATE TABLE Stadium (
    stadium_id tinyINT PRIMARY KEY AUTO_INCREMENT, -- Unique identifier for each stadium
    stadium_name VARCHAR(50) NOT NULL,        -- Name of the stadium
    city VARCHAR(50) NOT NULL,                -- City where the stadium is located
    country VARCHAR(25) NOT NULL              -- Country where the stadium is located
);

-- Create Game table
CREATE TABLE Game (
    game_id tinyint PRIMARY KEY AUTO_INCREMENT,    -- Unique identifier for each game
    game_type VARCHAR(25) check (game_type in ("Semi_finals", "Finals", "Group","Knockout", "Quarter_finals","Third_Place")),                     -- Type of game (e.g., group stage, final)
    game_date DATE,                            -- Date the game is played
    referee VARCHAR(50),                      -- Main referee for the game
    assistant_referee1 VARCHAR(50),           -- First assistant referee
    assistant_referee2 VARCHAR(50),           -- Second assistant referee
    fourth_official VARCHAR(50),              -- Fourth official
    var VARCHAR(50),                          -- Video Assistant Referee (VAR)
    offside_var VARCHAR(50),                  -- VAR for offside decisions
    assistant_var VARCHAR(50),                -- Assistant VAR
    support_var VARCHAR(50),                  -- Support VAR
    reserve_assistant_referee VARCHAR(50),    -- Reserve assistant referee
    attendance INT,                            -- Number of spectators attending the game
    weather VARCHAR(25) check (weather in ("Cloudy","Rainy","Sunny","Partly_Cloudy","Snow")),                      -- Weather during the game (e.g., sunny, rainy)
    stadium_id tinyINT,                            -- Foreign key to the Stadium table
    FOREIGN KEY (stadium_id) REFERENCES Stadium(stadium_id) -- Ensures valid stadium reference
);

-- Create Player table
CREATE TABLE Player (
    player_id smallint PRIMARY KEY AUTO_INCREMENT,  -- Unique identifier for each player
    player_name VARCHAR(50),
    birthdate DATE NOT NULL,                   -- Player's birth date
    jersey_number INT,                         -- Player's jersey number
    position VARCHAR(25) check (position in ("Goalkeeper","Midfielder","Attack","Defender")),                      -- Playing position (e.g., Forward, Midfielder)
    team_id tinyINT,                               -- Foreign key to the Team table
    FOREIGN KEY (team_id) REFERENCES Team(team_id) -- Ensures valid team reference
);

-- Create TV_Channel table
CREATE TABLE TV_Channel (
channel_id smallINT PRIMARY KEY AUTO_INCREMENT ,
channel_name VARCHAR(25) ,          -- Unique identifier for a TV channel (name)
    country VARCHAR(25) NOT NULL,             -- Country where the TV channel is based or operates
    channel_language VARCHAR(25) NOT NULL             -- Language of the TV broadcast
);


-- Create Team_Products weak entity table
CREATE TABLE Team_Products (
    team_id tinyINT,                              -- Foreign key from Team table
    product_id INT,                           -- Product ID
    size varchar(3) check (size in ("XXS", "XS", "S", "M", "L", "XL", "XXL")),                         -- Size of the product
    color VARCHAR(50),                        -- Color of the product
    price DECIMAL(10, 2),                     -- Price of the product
    PRIMARY KEY (team_id, product_id),        -- Composite primary key
    FOREIGN KEY (team_id) REFERENCES Team(team_id)  -- Foreign key to Team table
);

-- Create TV_Channel_Game bridge entity table
CREATE TABLE TV_Channel_Game (
    game_id tinyINT,                              -- Foreign key from Game table
    channel_id smallint,                  -- Foreign key from TV_Channel table
    PRIMARY KEY (game_id, channel_id),        -- Composite primary key
    FOREIGN KEY (game_id) REFERENCES Game(game_id),   -- Foreign key to Game table
    FOREIGN KEY (channel_id) REFERENCES TV_Channel(channel_id) -- Foreign key to TV_Channel table
);

-- Create Game-Players bridge entity table
CREATE TABLE Game_Players (
    game_id tinyINT,                              -- Foreign key from Game table
    player_id smallINT, -- Foreign key from Player table
    start_time TIME,                          -- Start time of the player in the game
    end_time TIME,                            -- End time of the player in the game
    yellow_cards tinyINT,                         -- Number of yellow cards received
    red_cards tinyINT,                            -- Number of red cards received
    passes smallINT,                               -- Number of passes made
    goals tinyINT,                                -- Number of goals scored
    assists tinyINT,                              -- Number of assists made
    offsides smallINT,                             -- Number of offsides committed
    PRIMARY KEY (game_id, player_id),         -- Composite primary key
    FOREIGN KEY (game_id) REFERENCES Game(game_id), -- Foreign key to Game table
    FOREIGN KEY (player_id) REFERENCES Player(player_id) -- Foreign key to Player table
);

-- Create Team-Game bridge entity table
CREATE TABLE Team_Game (
    team_id tinyINT,                              -- Foreign key from Team table
    game_id tinyINT,                             -- Foreign key from Game table
    formation VARCHAR(10),                    -- Formation used by the team in the game
    possession tinyint,                 -- Percentage of possession (e.g., 60%)
    corners tinyINT,                              -- Number of corner kicks
    free_kicks tinyINT,                           -- Number of free kicks
    penalties tinyINT,                            -- Number of penalties
    PRIMARY KEY (team_id, game_id),          -- Composite primary key
    FOREIGN KEY (team_id) REFERENCES Team(team_id),  -- Foreign key to Team table
    FOREIGN KEY (game_id) REFERENCES Game(game_id)  -- Foreign key to Game table
);

-- Insert mock data into Team table with team_name
INSERT INTO Team (team_name, group_name, coach_name, coach_nationality) VALUES
('United States', 'A', 'Jill Ellis', 'USA'),
('Germany', 'B', 'Martina Voss', 'GER'),
('Brazil', 'C', 'Pia Sundhage', 'BRA'),
('Netherlands', 'D', 'Sarina Wiegman', 'NED'),
('Spain', 'A', 'Jorge Vilda', 'ESP'),
('France', 'B', 'Corinne Diacre', 'FRA'),
('Sweden', 'C', 'Tony Gustavsson', 'SWE'),
('Canada', 'D', 'Beverly Priestman', 'CAN'),
('Nigeria', 'A', 'Randy Waldrum', 'NGA'),
('Norway', 'B', 'Hege Riise', 'NOR'),
('England', 'C', 'Mark Parsons', 'ENG'),
('New Zealand', 'D', 'Tom Sermanni', 'NZL'),
('Morocco', 'A', 'Vlatko Andonovski', 'USA'),
('Czech Republic', 'B', 'Jitka Klimkova', 'CZE'),
('Italy', 'C', 'Maren Meinert', 'GER');

INSERT INTO Stadium (stadium_name, city, country) VALUES
('Wembley Stadium', 'London', 'England'),
('Maracanã Stadium', 'Rio de Janeiro', 'Brazil'),
('Stade de France', 'Paris', 'France'),
('Camp Nou', 'Barcelona', 'Spain'),
('Allianz Arena', 'Munich', 'Germany'),
('San Siro', 'Milan', 'Italy'),
('Old Trafford', 'Manchester', 'England'),
('MetLife Stadium', 'New Jersey', 'USA'),
('Estadio Azteca', 'Mexico City', 'Mexico'),
('Krestovsky Stadium', 'St. Petersburg', 'Russia'),
('Olympic Stadium', 'Athens', 'Greece'),
('Signal Iduna Park', 'Dortmund', 'Germany'),
('Rose Bowl', 'Pasadena', 'USA'),
('Nelson Mandela Bay Stadium', 'Port Elizabeth', 'South Africa'),
('Moses Mabhida Stadium', 'Durban', 'South Africa');

INSERT INTO Game (game_type, game_date, referee, assistant_referee1, assistant_referee2, fourth_official, var, offside_var, assistant_var, support_var, reserve_assistant_referee, attendance, weather, stadium_id) VALUES
('Group', '2023-07-10', 'Martin Atkinson', 'Mark Clattenburg', 'Stuart Attwell', 'Bjorn Kuipers', 'Anthony Taylor', 'Felix Brych', 'Michael Oliver', 'Peter Walton', 'Steve Bennett', 65000, 'Sunny', 1),
('Group', '2023-07-11', 'Michael Oliver', 'Mike Dean', 'Howard Webb', 'Stuart Attwell', 'Clement Turpin', 'Bas Nijhuis', 'Paul Tierney', 'Gianluca Rocchi', 'Daniele Orsato', 70000, 'Cloudy', 2),
('Group', '2023-07-12', 'Felix Brych', 'Paul Tierney', 'Danny Makkelie', 'Mark Clattenburg', 'Sian Massey', 'Anthony Taylor', 'Stuart Attwell', 'Bjorn Kuipers', 'Steve Bennett', 72000, 'Rainy', 3),
('Knockout', '2023-07-14', 'Anthony Taylor', 'Michael Oliver', 'Stuart Attwell', 'Mike Dean', 'Peter Walton', 'Howard Webb', 'Felix Brych', 'Clement Turpin', 'Bjorn Kuipers', 80000, 'Partly_Cloudy', 4),
('Knockout', '2023-07-15', 'Sian Massey', 'Paul Tierney', 'Howard Webb', 'Anthony Taylor', 'Mike Dean', 'Stuart Attwell', 'Michael Oliver', 'Peter Walton', 'Gianluca Rocchi', 68000, 'Sunny', 5),
('Quarter_finals', '2023-07-17', 'Paul Tierney', 'Bjorn Kuipers', 'Felix Brych', 'Martin Atkinson', 'Howard Webb', 'Stuart Attwell', 'Sian Massey', 'Michael Oliver', 'Daniele Orsato', 75000, 'Cloudy', 6),
('Quarter_finals', '2023-07-18', 'Mike Dean', 'Stuart Attwell', 'Anthony Taylor', 'Mark Clattenburg', 'Peter Walton', 'Howard Webb', 'Michael Oliver', 'Paul Tierney', 'Felix Brych', 83000, 'Rainy', 1),
('Semi_finals', '2023-07-19', 'Martin Atkinson', 'Michael Oliver', 'Peter Walton', 'Anthony Taylor', 'Sian Massey', 'Mike Dean', 'Stuart Attwell', 'Felix Brych', 'Paul Tierney', 87000, 'Sunny', 2),
('Semi_finals', '2023-07-20', 'Danny Makkelie', 'Paul Tierney', 'Gianluca Rocchi', 'Bjorn Kuipers', 'Howard Webb', 'Clement Turpin', 'Bas Nijhuis', 'Michael Oliver', 'Peter Walton', 81000, 'Cloudy', 3),
('Finals', '2023-07-22', 'Bjorn Kuipers', 'Mike Dean', 'Anthony Taylor', 'Martin Atkinson', 'Stuart Attwell', 'Felix Brych', 'Michael Oliver', 'Howard Webb', 'Peter Walton', 92000, 'Sunny', 4),
('Third_Place', '2023-07-23', 'Paul Tierney', 'Clement Turpin', 'Daniele Orsato', 'Felix Brych', 'Michael Oliver', 'Bjorn Kuipers', 'Stuart Attwell', 'Sian Massey', 'Howard Webb', 68000, 'Rainy', 5),
('Group', '2023-07-08', 'Daniele Orsato', 'Bas Nijhuis', 'Clement Turpin', 'Mike Dean', 'Peter Walton', 'Martin Atkinson', 'Felix Brych', 'Howard Webb', 'Bjorn Kuipers', 54000, 'Partly_Cloudy', 6),
('Knockout', '2023-07-13', 'Bas Nijhuis', 'Howard Webb', 'Martin Atkinson', 'Peter Walton', 'Paul Tierney', 'Mike Dean', 'Stuart Attwell', 'Anthony Taylor', 'Michael Oliver', 79000, 'Sunny', 1),
('Quarter_finals', '2023-07-16', 'Michael Oliver', 'Stuart Attwell', 'Mark Clattenburg', 'Bjorn Kuipers', 'Sian Massey', 'Felix Brych', 'Paul Tierney', 'Daniele Orsato', 'Bas Nijhuis', 88000, 'Cloudy', 2),
('Finals', '2023-07-25', 'Mark Clattenburg', 'Anthony Taylor', 'Paul Tierney', 'Howard Webb', 'Felix Brych', 'Peter Walton', 'Stuart Attwell', 'Michael Oliver', 'Bjorn Kuipers', 95000, 'Sunny', 3);

INSERT INTO TV_Channel (channel_name, country, channel_language) VALUES
('BBC Sport', 'United Kingdom', 'English'),
('TF1', 'France', 'French'),
('Rede Globo', 'Brazil', 'Portuguese'),
('Fox Sports', 'United States', 'English'),
('Sky Sports', 'United Kingdom', 'English'),
('ESPN', 'United States', 'English'),
('Telecinco', 'Spain', 'Spanish'),
('ZDF', 'Germany', 'German'),
('BeIN Sports', 'Qatar', 'Arabic'),
('SBS', 'Australia', 'English'),
('Canal+', 'France', 'French'),
('RAI', 'Italy', 'Italian'),
('TV Azteca', 'Mexico', 'Spanish'),
('RTP', 'Portugal', 'Portuguese'),
('ORF', 'Austria', 'German');

INSERT INTO Team_Products (team_id, product_id, size, color, price) VALUES
(1, 1, 'M', 'Red', 49.99),
(2, 2, 'L', 'Blue', 59.99),
(3, 3, 'S', 'Green', 39.99),
(4, 4, 'XL', 'Black', 54.99),
(5, 1, 'M', 'White', 49.99),
(6, 2, 'L', 'Yellow', 59.99),
(7, 3, 'S', 'Orange', 39.99),
(8, 4, 'M', 'Purple', 54.99),
(9, 1, 'XL', 'Pink', 49.99),
(10, 2, 'L', 'Gray', 59.99),
(11, 3, 'M', 'Navy', 39.99),
(12, 4, 'S', 'Teal', 54.99),
(13, 1, 'L', 'Brown', 49.99),
(14, 2, 'XL', 'Black', 59.99),
(15, 3, 'M', 'Blue', 39.99);

INSERT INTO TV_Channel_Game (game_id, channel_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(1, 7),
(2, 8),
(3, 9),
(4, 10),
(5, 11),
(6, 12),
(1, 13),
(2, 14),
(3, 15);

-- Insert mock data into Player table
INSERT INTO Player (player_name, birthdate, jersey_number, position, team_id) VALUES
('Megan Rapinoe', '1995-07-12', 10, 'Midfielder', 1),
('Manuel Neuer', '1992-03-15', 1, 'Goalkeeper', 2),
('Neymar Jr', '1998-04-30', 7, 'Attack', 3),
('Virgil van Dijk', '1997-01-25', 4, 'Defender', 4),
('Sergio Busquets', '1999-09-19', 8, 'Midfielder', 5),
('Kylian Mbappe', '1993-06-28', 9, 'Attack', 6),
('Thiago Silva', '2000-05-11', 3, 'Defender', 7),
('Christine Sinclair', '1994-08-14', 11, 'Midfielder', 8),
('Asisat Oshoala', '1991-02-17', 2, 'Goalkeeper', 9),
('Ada Hegerberg', '1996-12-20', 5, 'Defender', 10),
('Alex Morgan', '1995-07-12', 10, 'Attack', 11),
('Saki Kumagai', '1997-03-23', 6, 'Midfielder', 12),
('Lindsey Horan', '1992-05-29', 1, 'Goalkeeper', 13),
('Fran Kirby', '1998-11-04', 7, 'Attack', 14),
('Sam Kerr', '2001-01-15', 8, 'Defender', 15);

-- Insert mock data into Team_Game table
INSERT INTO Team_Game (team_id, game_id, formation, possession, corners, free_kicks, penalties) VALUES
(1, 1, '4-4-2', 60, 5, 12, 1),
(2, 2, '3-5-2', 45, 3, 8, 0),
(3, 3, '4-3-3', 55, 6, 10, 2),
(4, 4, '4-2-3', 65, 7, 14, 3),
(5, 5, '5-4-1', 50, 4, 9, 1),
(6, 6, '4-4-2', 40, 3, 8, 0),
(7, 1, '4-3-3', 62, 4, 11, 1),
(8, 2, '4-5-1', 58, 6, 12, 0),
(9, 3, '3-4-3', 47, 2, 7, 2),
(10, 4, '4-4-2', 61, 5, 13, 1),
(11, 5, '5-3-2', 48, 6, 14, 2),
(12, 6, '4-4-2', 42, 4, 9, 1),
(13, 7, '3-5-2', 57, 6, 12, 1),
(14, 7, '4-2-3', 65, 7, 14, 2),
(15, 8, '3-4-3', 55, 8, 11, 0);

INSERT INTO Game_Players (game_id, player_id, start_time, end_time, yellow_cards, red_cards, passes, goals, assists, offsides) VALUES
(1, 1, '18:00:00', '19:20:00', 0, 0, 70, 1, 2, 0),
(2, 2, '18:10:00', '19:30:00', 1, 0, 32, 1, 1, 1),
(3, 3, '18:05:00', '19:25:00', 0, 0, 40, 0, 0, 2),
(4, 4, '18:00:00', '19:30:00', 1, 0, 55, 1, 2, 1),
(5, 5, '18:20:00', '19:30:00', 0, 0, 62, 2, 0, 0),
(6, 6, '18:10:00', '19:15:00', 2, 0, 47, 1, 1, 1),
(7, 7, '18:00:00', '19:20:00', 0, 1, 30, 1, 2, 0),
(1, 8, '18:05:00', '19:30:00', 1, 0, 38, 0, 1, 1),
(2, 9, '18:15:00', '19:30:00', 0, 0, 44, 1, 0, 0),
(3, 10, '18:00:00', '19:30:00', 0, 1, 39, 0, 1, 2),
(4, 11, '18:10:00', '19:30:00', 2, 0, 50, 2, 0, 0),
(5, 12, '18:00:00', '19:15:00', 0, 0, 25, 0, 1, 0),
(6, 13, '18:20:00', '19:30:00', 0, 0, 60, 1, 0, 0),
(7, 14, '18:00:00', '19:10:00', 1, 0, 42, 0, 2, 1),
(1, 15, '18:00:00', '19:30:00', 0, 0, 55, 1, 0, 1);
