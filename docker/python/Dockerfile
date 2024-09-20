FROM ubuntu:20.04
USER root

WORKDIR /app
COPY requirements.txt ${pwd}

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update -y
RUN apt upgrade -y
RUN apt dist-upgrade -y
RUN apt autoremove -y
RUN apt autoclean -y

# Python 3.10用のPPAを追加してインストール
RUN apt install -y gnupg2 curl
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install python3.10 -y
RUN apt update -y
RUN apt install -y libgl1-mesa-dev
RUN apt remove python-pip
RUN apt install python3.10-distutils -y
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
RUN pip install -r requirements.txt

# pythonコマンドの参照先をPython3.10に変更
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

#for flask
ENV FLASK_APP=app.py
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["flask","run"]
