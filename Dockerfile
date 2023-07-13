FROM python:3.10.11-bullseye
ADD . /app
WORKDIR /app

RUN pip install langchain openai PyGithub cffi cryptography python-dotenv

ENV PYTHONPATH /app
CMD ["python3", "/app/main.py", "github_action"]