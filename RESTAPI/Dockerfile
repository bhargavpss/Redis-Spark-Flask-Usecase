FROM centos:centos7

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py && \
    pip install flask redis --user


WORKDIR app/

ENV PATH $PATH:~/.local/bin

COPY flaskrest.py .

CMD python flaskrest.py
