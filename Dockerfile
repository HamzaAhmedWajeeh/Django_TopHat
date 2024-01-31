FROM python:3.10-slim
LABEL maintainer="TopHat"

ENV PYTHONUNBUFFERED=1


EXPOSE 8000

RUN apt-get update
# Install neccessory Packages for building wheel of python
RUN apt-get install -y build-essential libffi-dev libssl-dev curl

# Install the Microsoft ODBC driver Linux. Follow the mssql documentation: https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

# Create a non-root user
RUN adduser --disabled-password django-user

# Copy requirements for dev and prod
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.txt /tmp/requirements.txt

# Install packages
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt

# Install development packages if DEV=true in docker-compose
# RUN if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt; fi

COPY ./scripts /scripts

# Create directories for static and media files & set permissions
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN chown -R django-user:django-user /vol
RUN chmod -R 755 /vol && chmod -R +x /scripts

ENV PATH="/scripts:/py/bin:$PATH"

COPY ./app /app
WORKDIR /app
RUN chown -R django-user:django-user /app

USER django-user

CMD ["run.sh"]