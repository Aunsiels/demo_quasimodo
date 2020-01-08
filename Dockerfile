from ubuntu:latest

RUN apt update -yqq \
    && apt upgrade -yqq \
    && apt install -y unzip \
        python3 python3-pip \
        fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
        libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
        curl unzip wget \
        xvfb \
    && rm -rf /var/lib/apt/lists/*  

# install geckodriver and firefox
# (from https://github.com/dimmg/dockselpy)

RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP


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
