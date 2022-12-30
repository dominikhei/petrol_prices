import requests
from jsonschema import validate
from api_schema import schema
import sys
import time
from datetime import datetime
from datetime import date
import pandas as pd
from test_dict import transformation_test_dict
import mysql.connector
from mysql.connector import errorcode


def load_from_api(key: str):
    api_link = "https://creativecommons.tankerkoenig.de/json/list.php?lat=47.997791&lng=7.842609&rad=10&sort=price&type=e5&apikey=" + key

    try:
        response = requests.get(api_link)
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting, check your internet connection:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error, will retry in 1 min:", errt)
        time.sleep(60)
        load_from_api(key)

    global petrol_data
    petrol_data = response.json()['stations']

    for element in petrol_data:
        if not element['isOpen']:
            petrol_data.remove(element)


def transform(data: list):

    global stations_df
    stations_df = pd.DataFrame(data)

    stations_df = stations_df[['id', 'name', 'price', 'street', 'houseNumber']]
    stations_df['date'] = date.today()
    stations_df['time'] = datetime.now().strftime("%H:%M")

    stations_df.dropna(inplace=True)
    stations_df.drop_duplicates(subset='id', keep="first", inplace=True)
    stations_df.reset_index(drop=True, inplace=True)

    for i in range(len(stations_df)):
        if (stations_df['price'][i] > 2 * stations_df['price'].mean()) | (
                stations_df['price'][i] < 0.2 * stations_df['price'].mean()):
            stations_df.drop([i], axis=0, inplace=True)
    stations_df.reset_index(drop=True, inplace=True)

    for i in range(len(stations_df)):
        if len(stations_df['id'][i]) != 36:
            stations_df.drop([i], axis=0, inplace=True)
    stations_df.reset_index(drop=True, inplace=True)

    return stations_df


def test_transform():

    test_transformation_result = transform(transformation_test_dict)
    test_transformation_result.drop(['time', 'houseNumber', 'street'], axis=1, inplace=True)

    result_data = {'id': ['00060780-0001-4444-8888-acdc00000001', '94f3da38-8a15-49c5-bc5d-4a73c47cba3c'],
                   'name': ['abcd', 'Total1'],
                   'price': [2.0, 2.0],
                   'date': [date.today(), date.today()]}
    expected_transformation_result = pd.DataFrame(result_data)

    try:
        pd.testing.assert_frame_equal(test_transformation_result, expected_transformation_result)
    except Exception as e:
        print('Unit test was not successful, due to error:', e)
        sys.exit(1)
    print("Passed the Unit test for the transformation function")


# This will offer a simple api-integration test,
# checking the response code, response header and the response json-format of a sample get request
def api_tests(key: str):

    try:
        response = requests.get(
            "https://creativecommons.tankerkoenig.de/json/list.php?lat=47.997791&lng=7.842609&rad=1&sort=price&type=e5&apikey=" + key)
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting, check your internet connection:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error, will retry in 1 min:", errt)
        time.sleep(60)
        api_tests(key)

    try:
        assert response.status_code == 200
    except AssertionError:
        print('Wrong response code, the response code is:', response.status_code)
        sys.exit(1)

    # Validate response content type header
    try:
        assert response.headers["Content-Type"] == "application/json; charset=utf-8"
    except AssertionError:
        print('Wrong response header')
        sys.exit(1)

    resp_body = response.json()['stations']

    # Validate will raise exception if given json is not
    # what is described in schema.
    try:
        validate(instance=resp_body, schema=schema)
    except Exception as e:
        print(e)
        sys.exit(1)
    print("Passed the API Integration test")


def establish_db_connection():

    try:
        global cnx
        global db_cursor
        cnx = mysql.connector.connect(user='root',
                                      password='_____',
                                      host='host.docker.internal',
                                      port='3308',
                                      database='_____')
        db_cursor = cnx.cursor()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


def create_table():
    create_table = """CREATE TABLE IF NOT EXISTS petrol_data(
                      load_id BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                      id VARCHAR(36) NOT NULL,
                      name VARCHAR(100),
                      price FLOAT(4),
                      street Varchar(100),
                      houseNumber Varchar(20),
                      date DATE,
                      time Varchar(5));"""

    try:
        db_cursor.execute(create_table)
        cnx.commit()
    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        db_cursor.close()
        cnx.close()


def insert_to_database(data):
    cols = "`,`".join([str(i) for i in data.columns.tolist()])
    try:
        for i, row in data.iterrows():
            insert = "INSERT INTO `petrol_data` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
            db_cursor.execute(insert, tuple(row))
            cnx.commit()
    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        db_cursor.close()
        cnx.close()

def close_connection():

    db_cursor.close()
    cnx.close()

def etl_main(key: str):
    api_tests(key)
    load_from_api(key)
    test_transform()
    transform(petrol_data)
    establish_db_connection()
    create_table()
    insert_to_database(stations_df)
    close_connection()


if __name__ == "__main__":
    etl_main(key='______')

