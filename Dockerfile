FROM python:3.9
LABEL maintainer="Zarex Alvin Daria"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# command to run on container start
CMD [ "python", "__init__.py" ]
CMD [ "python", "app.py" ]
EXPOSE 3111