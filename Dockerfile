FROM python:3

ADD whos-out.py /
RUN chmod +x /whos-out.py
RUN pip3 install requests pandas