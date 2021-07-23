FROM python:3.7
COPY requirements.txt .
RUN python3 -m venv .venv
RUN . ./.venv/bin/activate 
RUN pip install -r requirements.txt
COPY . .
ENV SQL_URI="mysql+pymysql://root:root@database:3306/todo
EXPOSE 5000
ENTRYPOINT ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "app:app"]
