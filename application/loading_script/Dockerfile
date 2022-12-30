FROM python:3

ADD load_data.py /

ADD api_schema.py /

Add test_dict.py /

RUN pip install pandas datetime protobuf mysql-connector-python requests jsonschema

CMD ["python", "./load_data.py"]