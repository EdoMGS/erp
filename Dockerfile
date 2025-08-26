FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Install OS packages required by some Python deps (weasyprint/reportlab/lxml)
RUN apt-get update \
	 && apt-get install -y --no-install-recommends \
		 build-essential \
		 libffi-dev \
		 libxml2 \
		 libxslt1.1 \
		 libxslt1-dev \
		 libcairo2 \
		 libpango-1.0-0 \
		 libpangocairo-1.0-0 \
		 libjpeg62-turbo \
		 zlib1g \
		 libmagic1 \
		 git \
	 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code/