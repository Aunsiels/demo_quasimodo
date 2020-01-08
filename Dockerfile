from ubuntu:latest

RUN apt update -yqq \
    && apt upgrade -yqq \
    && apt install -y unzip \
       xvfb \
       libxi6 \
       libgconf-2-4 \
       default-jdk \
       firefox \
       python3-pip \
       wget \
    && rm -rf /var/lib/apt/lists/*  

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz \
    && tar xzf geckodriver*.tar.gz \
    && mv geckodriver /usr/bin/geckodriver

RUN pip3 install --upgrade pip

RUN pip3 install \
    flask-testing \
    selenium \
    pytest \
    flask \
    flask-bootstrap \
    flask-sqlalchemy \
    flask-migrate \
    flask-wtf \
    flask_fontawesome \
    pyvirtualdisplay
