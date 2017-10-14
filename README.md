# Log Analysis Project
Python / PostgresSQL project to print the answers to 3 questions to
the terminal:
1. What are the most popular three articles of all time?
2. Who are the most popular article authors of all time?
3. On which days did more than 1% of requests lead to errors?

## Requirements
- Python 3.x.x

## Installation / Execution
This program utilises 3 PSQL views. They are created at runtime
and DO NOT need to be created before running the program.

However, if for some reason they cannot be created at runtime,
please refer to the 3 queries below:

```
create or replace view log_404 as
select time::date as date, count(id) as error_count
from log
where status = '404 NOT FOUND'
group by date;
```

```
create or replace view log_grouped as
select time::date as date, count(id) as response_count
from log
group by date;
```

```
create or replace view log_error_summary as
select l1.date, l1.error_count, l2.response_count,
round((cast(l1.error_count as decimal) / l2.response_count) * 100, 1) as percentage_errors
from log_404 l1
join log_grouped l2 on l1.date = l2.date;
```

Run the program from project root as follows:

```
python3 main.py
```