import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import matplotlib.pyplot as plt
import numpy as np
from secret_variables import *


def establish_db_connection():

    global db_cursor
    global cnx

    try:
        cnx = mysql.connector.connect(user="__",
                                      password="___",
                                      host='host.docker.internal',
                                      port='3308',
                                      database="____")
        db_cursor = cnx.cursor(buffered=True)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


def average_now():

    result = []

    try:
        query = """SELECT price FROM petrol_data
                       WHERE time = (SELECT MAX(time) FROM petrol_data)
                       ORDER BY price ASC
                       LIMIT 1;"""
        db_cursor.execute(query)
        result = db_cursor.fetchall()
    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        db_cursor.close()
        cnx.close()

    price = result[0][0]
    return price


def average_last_24_h():

    query = """SELECT Avg(price) FROM petrol_data
               WHERE TIMESTAMP(date,time) > now() - interval 24 hour;"""

    avg_last_24_h = []

    try:
        db_cursor.execute(query)
        cnx.commit()
        avg_last_24_h.append(db_cursor.fetchall())
    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        db_cursor.close()
        cnx.close()

    price = avg_last_24_h[0][0][0]
    return price


def average_last_week():

    query = """SELECT AVG(price) FROM petrol_data
               WHERE date >= DATE(NOW()) - INTERVAL 7 DAY;"""

    avg_last_week = []
    try:
        db_cursor.execute(query)
        cnx.commit()
        avg_last_week.append(db_cursor.fetchall())

    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        db_cursor.close()
        cnx.close()

    price = avg_last_week[0][0][0]
    return price


def cheapest_station():

    test = []

    try:
        query = """SELECT name, price, time, street, houseNumber FROM petrol_data
                   WHERE time = (SELECT MAX(time) FROM petrol_data)
                   ORDER BY price ASC
                   LIMIT 1;               
                     """
        db_cursor.execute(query)
        test = db_cursor.fetchall()
    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        db_cursor.close()
        cnx.close()

    name = test[0][0]
    price = test[0][1]
    time = test[0][2]
    street = test[0][3]
    number = test[0][4]

    return name, price, time, street, number


def average_last_week_plot():

    prices = []
    times = []

    select_prices = """SELECT avg(price)
                       FROM petrol_data
                       GROUP BY SUBSTRING(time,1,5)
                       ORDER BY SUBSTRING(time,1,5) ASC;"""

    select_times = """SELECT SUBSTRING(time,1,5)
                      FROM petrol_data
                      GROUP BY SUBSTRING(time,1,5)
                      ORDER BY SUBSTRING(time,1,5) ASC;"""

    try:
        db_cursor.execute(select_prices)
        for i in db_cursor.fetchall():
            prices.append(i[0])

        db_cursor.execute(select_times)
        for i in db_cursor.fetchall():
            times.append(i[0])
    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        db_cursor.close()
        cnx.close()

    timeseries_data = {'times': times,
                       'prices': prices}
    dataframe = pd.DataFrame(timeseries_data, columns=['times', 'prices'])
    dataframe.set_index("times",inplace=True)

    return dataframe

