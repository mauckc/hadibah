drop table if exists users;
create table users (
  id integer primary key autoincrement,
  'name' text not null,
  'username' text not null,
  'password' text not null,
  'email' text not null
);
