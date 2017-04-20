drop table if exists current_plan;
create table current_plan (
  id integer primary key autoincrement,
  sms integer not null,
  calls float not null,
  data float not null);

drop table if exists current_usage;
create table current_usage (
  id integer primary key autoincrement,
  sms integer not null,
  calls float not null,
  data float not null);

drop table if exists conversion_table;
create table conversion_table (
	sms2call float not null,
	sms2data float not null,
	call2data float not null,
	call2sms float not null,
	data2call float not null,
	data2sms float not null);

drop table if exists event,
create table event (
	event_time date primary key not null,
	event_type text not null,
	'text' text not null);
