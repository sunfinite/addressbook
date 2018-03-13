drop table if exists contacts;
create table contacts (
  id integer primary key autoincrement,
  name text not null,
  email text not null,
  /* phone is text to allow multiple formats in the simplest way */
  phone text not null
);
