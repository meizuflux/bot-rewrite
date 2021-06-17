FROM python:3.9.5-slim-buster
LABEL maintainer="ppotatoo"

# make linux work
RUN apt-get update && \
    apt-get install -y git neofetch

# copy files and stuff
COPY requirements.txt /src/requirements.txt
WORKDIR /src
RUN pip install -r requirements.txt
COPY . .

# run the bot.
CMD ["python", "run.py", "--run"]