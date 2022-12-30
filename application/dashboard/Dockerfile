FROM python:3.9-slim

EXPOSE 8501

ADD streamlit_dashboard.py /

COPY requirements.txt .

ADD database_select_functions.py /

RUN pip3 install -r requirements.txt

CMD streamlit run streamlit_dashboard.py