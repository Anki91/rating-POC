--drop table if exists current_plan;
--create table current_plan (
--  id integer primary key autoincrement,
--  sms integer not null,
--  calls float not null,
--  data float not null);

drop table if exists current_usage;
create table current_usage (
  id integer primary key,
  sms float ,
  calls float ,
  data float);
insert into current_usage (id, sms, calls, data) values (1,0.0,0.0,0.0);


drop table if exists allowed_usage;
create table allowed_usage (
  id integer primary key,
  sms float not null,
  calls float not null,
  data float not null);

--drop table if exists conversion_table;
--create table conversion_table (
--	event_type text not null,
--	conversion_rate float not null);

drop table if exists event;
create table event (
	event_quantity float not null,
	event_type text not null,
	event_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
