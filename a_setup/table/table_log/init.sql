--  /a_setup/table/table_log/
--  sql 模板文件，记录本应用涉及的数据库表建表语法

--  users_log: 自带日志记录的单表
--  复制到SQL界面执行
drop table if exists users_log;
CREATE TABLE users_log
(
  id integer primary key autoincrement ,    -- 自增主键
  id_of_data integer,       -- 数据主键，需要此字段，name才可修改，否则name不可修改
  name character varying(20),   -- 姓名
  part character varying(100),  -- 部门
  state character varying(20),  -- 状态，可能为有效，注销，挂起
  action character varying(20), -- 动作，用于显示日志，取值为：新增，修改，删除
  mtime character varying(20),  -- 修改时间
  content character varying(200)    -- 备注
);
;