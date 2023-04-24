--  sqlite3 
--  cfg_tables init sql

CREATE
    TABLE
         if not exists CFG_TABLES (
            ID serial primary key NOT NULL ,
            KIND VARCHAR(40) ,
            NAME VARCHAR(100) ,
            NAME_ZH VARCHAR(40) ,
            DEMO VARCHAR(200) ,
            NAME_A VARCHAR(20) ,
            NAME_Z VARCHAR(20) ,
            ADD1 VARCHAR(100) ,
            ADD2 VARCHAR(100) ,
            ADD3 VARCHAR(100) ,
            ADD4 VARCHAR(100)
        )
