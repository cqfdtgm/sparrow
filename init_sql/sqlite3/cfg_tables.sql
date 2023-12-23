--  sqlite3 
--  cfg_tables init sql

CREATE
    TABLE
         if not exists cfg_tables (
            id INTeger primary key autoincrement NOT NULL ,
            kind VARCHAR(40) ,
            name VARCHAR(100) ,
            name_zh VARCHAR(40) ,
            demo VARCHAR(200) ,
            NAME_A VARCHAR(20) ,
            NAME_Z VARCHAR(20) ,
            ADD1 VARCHAR(100) ,
            ADD2 VARCHAR(100) ,
            ADD3 VARCHAR(100) ,
            ADD4 VARCHAR(100)
        )
