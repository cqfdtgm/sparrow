create table  if not exists org(
	id serial primary key ,
	text varchar(200),
	parentid integer not null,
	state varchar(20),
	display integer,
	path varchar(200),
	level  integer
				 )

