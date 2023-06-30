import sqlite3 as sl

"""
SELECT ('столбцы или * для выбора всех столбцов; обязательно')
FROM ('таблица; обязательно')
WHERE ('условие/фильтрация, например, city = 'Moscow'; необязательно')
GROUP BY ('столбец, по которому хотим сгруппировать данные; необязательно')
HAVING ('условие/фильтрация на уровне сгруппированных данных; необязательно')
ORDER BY ('столбец, по которому хотим отсортировать вывод; необязательно')
"""

con = sl.connect('auctions.db')

with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS Clients (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        full_name TEXT, 
        phone_number TEXT, 
        adress TEXT,
        wailet BIGINEGER
        try_strike INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS Administration (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        status TEXT
        phone INTEGER
        address TEXT
        login TEXT
        password TEXT
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS Accept_lot (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER,
        accept_status TEXT,
        lots_id BIGINTEGER,
        FOREIGN KEY (admin_id) REFERENCES Administration (id),
        FOREIGN KEY (lots_id) REFERENCES Lots (id)
        )
        """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS Lots (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        descriptions TEXT, 
        start_price INTEGER,
        link_seller TEXT,
        photo TEXT,
        geolocations TEXT,
        start_time DATETIME,
        end_time DATETIME
        )
        """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS Traids (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        lots_id BIGINTEGER,
        trade_info TEXT,
        traids_status BIGINTEGER,
        FOREIGN KEY (lots_id) REFERENCES Lots (id)
        )
    """)
