### Base stage
FROM python:3.11-alpine AS base-stage

ENV FLASK_APP=app.py

RUN adduser --disabled-password --home /app --shell /bin/bash app

USER app
WORKDIR /app

COPY requirements.txt ./

RUN echo "export PATH=${PATH}:/app/.local/bin" >> .bashrc


### Development stage
FROM base-stage AS development-stage

ENV APP_ENV=dev

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

### Build stage
FROM base-stage AS build-stage

COPY spot_belpex.py /app
COPY wsgi.py /app

RUN pip install --no-cache-dir -r requirements.txt

### Production stage
FROM build-stage AS production-stage

COPY --from=build-stage /app /app

EXPOSE 81

CMD ["/app/.local/bin/gunicorn", "--access-logfile", "-", "--workers=3", "-b", "0.0.0.0:8000", "wsgi:app"]