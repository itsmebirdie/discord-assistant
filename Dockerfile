From python:3.8
LABEL maintainer="0xbirdie@gmail.com"

ADD . .
RUN apt update && apt-get -y install sudo
RUN sudo apt install ffmpeg
RUN pip install discord.py[voice] requests dpymenus youtube_dl

CMD [ "python3", "./main.py" ]
