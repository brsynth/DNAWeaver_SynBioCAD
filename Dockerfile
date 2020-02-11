FROM python:3.6


# Install everything
RUN apt-get -qq update \
 && apt-get install -y ncbi-blast+

WORKDIR /home/

COPY requirements.txt /home
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

COPY docs /home/docs
COPY methods /home/methods
COPY script.py /home
COPY test_input.xml /home
COPY example_output.xlsx /home
COPY tests.py /home

COPY rpToolServe.py /home/
COPY rpTool.py /home/

ENTRYPOINT ["python"]
CMD ["/home/rpToolServe.py"]

# Open server port
EXPOSE 8888
