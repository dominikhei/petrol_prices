# Overview

Since petrol prices have been at an all time high recently, I wondered whether there is a pattern in prices, how current prices are, compared to last weeks / yesterdays and wanted to know which station in my hometown of Freiburg is the cheapest.

Therefore I have developed this containerized application, consisting of an etl-script loading data into a mysql database and a Dashboard which presents the data in a visually pleasing manner. All of the different services are deployed using docker-compose. Data is extracted and loaded every 20 minutes using Apache Airflow.

### Architecture

![](https://github.com/dominikhei/petrol_prices/blob/master/images/petrol.png)

### Used technologies:

- MySQL
- Docker with docker-compose
- Apache Airflow
- Tankerkoenig API
- Python 
- Streamlit library for the dashboard

# Different services

### Database 
I am using a MySQL database, in a docker container to store the data on the petrol prices. It will always keep on running, even when the loading functionalities container gets killed after execution. When pulling this project you have to set your own database access variables, like db_name and root_password in the docker-compose.yml file and the part of the loading script where you are connecting to the database.  When running the container for the first time the create-table.sql file gets executed and the table to hold the data will be created, if it does not already exist.

### Apache Airflow

To extract, transform and load the data I am using airflow. The dag will be executed every 20 minutes and can be found here. I am using the docker operator to run a container based on the image for the python_app. Once a container has been executed, it will be killed automatically. 

### Streamlit Dashboard

__INSERT IMAGE OF THE DASHBOARD__

As already stated it was also important to me to present my findings in a simple and concise manner. I figured the best solution would be a web dashboard which can be accessed via the hosts 8501 port in your browser under: http://localhost:8501/ due to port mapping.
Just like the rest it will be automatically executed with docker-compose once you "start" the whole application.  The Dashboard present insights on the following questions:

- Price distribution overt the day (average of last 7 days used)
- Which is the current cheapest gas station
- How are the gas prices currently compared to either yesterday's average or the last 7 days average

The streamline script is making use of several functions from the database_select_functions.py file which are making the actual database select statements and returning the results. This is making sure everything is neatly and separated by splitting the presentation and the model.
The Docker image is built with streamlit version 1.9.0, because the newest one does not work very well with docker. 


### Etl functions

The data on the petrol prices is being fetched from an [Api](https://creativecommons.tankerkoenig.de). Once it is returned, i transform the format from JSON to a pandas dataframe and drop columns I do not need, as well as checking for Na's, duplicates and values that do not make sense. The remaining rows will then be loaded into a MySQL table. __The get-request and the data transformations will be tested beforehand__

**Tests**

Before the api request will be made, I am executing an integration test, which tests for two things:
- Response code from the api
- Wheter the returned data in Json format meets the expected format (aka.has the same keys at the same places), with the validate function from the jsonschema package. The Json schema for the test can be found [here](https://github.com/dominikhei/petrol_prices/blob/master/application/loading_script/api_schema.py)
When these tests are successfull the actual request will be made. If not, the script terminates.

In advance of the transformations with the returned data from the api, a unit test for the transformation function will be executed. There the transformation function will be called on a sample dataframe, which has all the flaws for which the function checks. If it meets an expected outcome after the transformation, the test was succesfull and the function will be called on the actual data. If not, the script terminates. 

The whole Etl process consists of 9 functions. 
All of them are bundled into one main function, which is protected from being invoked through an import, and is executed automatically when a docker container is started. 


### Deployment using Docker

I have used docker for the project to ensure that it runs on every machine. 
Since the application consists of 3 services, it is built as a multi-container application with docker-compose. The 3 different services are defined in the [docker-compose.yml](https://github.com/dominikhei/petrol_prices/blob/master/application/docker-compose.yml) file. It can be executed by navigating into the [application](https://github.com/dominikhei/petrol_prices/tree/master/application) folder via the command line and there using the command: docker-compose up, which builds the three images and starts containers based on these simultainously.


# How to run the project on your machine 

To run the project on your machine, you need docker and Apache-Airflow installed and a token for the Tankerkoenig Api. 
The Api token can be obtained [here](https://creativecommons.tankerkoenig.de)
The dag from the [airflow_dag](https://github.com/dominikhei/petrol_prices/blob/master/airflow_dag/petrol_etl_dag.py) folder has to be moved into Airflows dags folder. Once that has been done you should navigate into the [application](https://github.com/dominikhei/petrol_prices/tree/master/application) folder and execute the docker-compose up command once. All three services will be started from there. 
