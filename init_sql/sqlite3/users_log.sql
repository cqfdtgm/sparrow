--  users_log.sql

CREATE TABLE  if not exists users_log
(
  id integer primary key autoincrement ,
  did integer,
  name character varying(20),
  action character varying(20),
  stime character varying(20),
  ip character varying(20),
  content character varying(200)
)