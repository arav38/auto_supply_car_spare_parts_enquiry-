from sqlalchemy import create_engine
import urllib


import pyodbc
print(pyodbc.drivers())



def sql_connect():

        # Set up the connection string
    server = 'DESKTOP-GF47VQO'  # Replace with your server name
    database = 'MyDatabase'  # Replace with your database name
    username = 'Akshay'  # Replace with your SQL Server username
    password = '6644'  # Replace with your SQL Server password

    # Encode the connection string using urllib
    params = urllib.parse.quote_plus(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                                    f'SERVER={server};'
                                    f'DATABASE={database};'
                                    f'UID={username};'
                                    f'PWD={password}')

    # Create an engine for connecting to SQL Server
    engine = create_engine(f'mssql+pyodbc:///?odbc_connect={params}')

    print(engine)

    return engine

db = sql_connect()

print(db)












# CREATE TABLE Users (
#     UserID INT PRIMARY KEY IDENTITY(1,1),   -- Unique User ID, auto-increment
#     FullName NVARCHAR(100) NOT NULL,         -- Full Name of the user
#     EmailAddress NVARCHAR(100) NOT NULL,     -- User's email address
#     ContactNumber NVARCHAR(20) NOT NULL,     -- User's contact number
#     Username NVARCHAR(50) NOT NULL,          -- Username chosen by the user
#     Password NVARCHAR(255) NOT NULL,         -- Password (hashed or plain-text; ideally hashed)
#     Role NVARCHAR(20) NOT NULL,              -- User's role (Customer/Supplier)
#     CONSTRAINT UQ_Username UNIQUE (Username),  -- Ensure unique usernames
#     CONSTRAINT UQ_EmailAddress UNIQUE (EmailAddress) -- Ensure unique email addresses
# );
