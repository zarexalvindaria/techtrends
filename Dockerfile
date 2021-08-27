FROM python:3.9
LABEL maintainer="Zarex Alvin Daria"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# create the database
RUN python init_db.py

# command to run on container start
CMD [ "python", "app.py" ]
EXPOSE 3111