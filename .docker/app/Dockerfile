FROM python:3

RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

RUN wget https://storage.googleapis.com/chrome-for-testing-public/130.0.6723.116/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip -d /usr/bin/

RUN apt update \
    && apt install -y vim \
    fonts-ipaexfont-gothic \
    fonts-ipaexfont-mincho \
    google-chrome-stable \
    && apt clean

WORKDIR /var/www/app
COPY requirements.txt ./
RUN pip install -r requirements.txt

ENV PYTHONIOENCODING utf-8
ENV TZ="Asia/Tokyo"
ENV LANG=C.UTF-8
ENV LANGUAGE=en_US:en_US

CMD ["/bin/bash"]
