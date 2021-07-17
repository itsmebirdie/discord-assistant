From python:3.8
LABEL maintainer="0xbirdie@gmail.com"

ADD . .
RUN sudo apt update
RUN sudo apt install ffmpeg
RUN pip install discord.py[voice] requests dpymenus youtube_dl

CMD [ "python3", "./main.py" ]
