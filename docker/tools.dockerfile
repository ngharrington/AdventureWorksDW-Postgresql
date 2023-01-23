FROM python:3.11.1-slim


COPY ./tools/tools-requirements.txt /app/tools-requirements.txt
COPY ./docker/files/odbcinst.ini /opt/odbc/odbcinst.ini

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y unixodbc unixodbc-dev curl gnupg

# Add SQL Server ODBC Driver 17 for Ubuntu 18.04
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

RUN python -m pip install -r /app/tools-requirements.txt

WORKDIR /app
