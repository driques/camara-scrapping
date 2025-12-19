FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN playwright install chromium
RUN playwright install-deps

COPY ./main.py /code/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
