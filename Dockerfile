FROM python:3.6-alpine
LABEL maintainer="Victor Gonzalez <isc.victor.gonzalez@live.com.mx>"
ENV PS1="\[\e[0;33m\]|> myredpy <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "

WORKDIR /src
COPY . /src
RUN pip install --no-cache-dir -r requirements.txt \
  && python setup.py install
WORKDIR /
ENTRYPOINT ["myredpy"]
