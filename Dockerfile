FROM pypy:2-2.5.0
MAINTAINER Simon de Haan <simon@praekeltfoundation.org>
COPY . /var/springboard/
WORKDIR /var/springboard/
RUN pip install -e .
WORKDIR /var/
RUN springboard startapp myapp
VOLUME /var/myapp
EXPOSE 6543
CMD pserve development.ini --reload
