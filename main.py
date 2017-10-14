#!/usr/bin/env python3

import psycopg2


def display_rows(template, res):
    """
    Print rows from SQL query using specified template.
    Note: Assumes each row has 2 columns
    :param template:
    :param res:
    """
    for row in res:
        print(template.format(row[0], row[1]))

    print("\r\n")


def create_views(cursor):
    """
    Setup views for queries that require them.
    :param cursor:
    """
    cursor.execute(
        "create or replace view log_404 as "
        "select time::date as date, count(id) as error_count "
        "from log "
        "where status = '404 NOT FOUND' "
        "group by date;"
    )

    cursor.execute(
        "create or replace view log_grouped as "
        "select time::date as date, count(id) as response_count "
        "from log "
        "group by date;"
    )

    cursor.execute(
        "create or replace view log_error_summary as "
        "select l1.date, l1.error_count, l2.response_count, "
        "round((cast(l1.error_count as decimal) / l2.response_count) *100, 1) "
        "as percentage_errors "
        "from log_404 l1 "
        "join log_grouped l2 "
        "on l1.date = l2.date;"
    )


# Setup DB connection and call function to create required views
conn = psycopg2.connect("dbname=news user=vagrant")
cur = conn.cursor()
create_views(cur)


# Execute / display query to answer question:
# 1. What are the most popular three articles of all time?
cur.execute(
    "select a.title, count(a.id) as views "
    "from articles a "
    "join log l on concat('/article/', a.slug) = l.path "
    "group by a.title "
    "order by views desc "
    "limit 3;"
)

print("\n\r1. What are the most popular three articles of all time? \n\r")
display_rows("  * {} - {} views", cur.fetchall())


# Execute / display query to answer question:
# 2. Who are the most popular article authors of all time?
cur.execute(
    "select aa.name, count(aa.id) as views "
    "from authors aa "
    "join articles a on a.author = aa.id "
    "join log l on concat('/article/', a.slug) = l.path "
    "group by aa.name "
    "order by views desc;"
)

print("2. Who are the most popular article authors of all time? \n\r")
display_rows("  * {} - {} views", cur.fetchall())


# Execute / display query to answer question:
# 3. On which days did more than 1% of requests lead to errors?
cur.execute(
    "select to_char(l.date, 'FMMonth DD, YYYY') as date, l.percentage_errors "
    "from log_error_summary l "
    "where percentage_errors >= 1;"
)

print("3. On which days did more than 1% of requests lead to errors? \n\r")
display_rows("  * {} - {}% errors", cur.fetchall())


# Cleanup
cur.close()
conn.close()
