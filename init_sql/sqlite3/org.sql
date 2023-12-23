create table  if not exists org(
	id integer primary key autoincrement,
	text varchar(200),
	parentid int not null,
	state varchar(20),
	display integer,
	path varchar(200),
	level integer
				 )

