FROM ubuntu:latest
WORKDIR /judge
RUN apt-get update && apt-get install -y gcc g++
COPY run.sh /judge
RUN mkdir input
RUN chmod +x run.sh
CMD ./run.sh
