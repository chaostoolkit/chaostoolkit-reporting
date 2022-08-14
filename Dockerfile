FROM ubuntu:latest

LABEL maintainer="chaostoolkit <contact@chaostoolkit.org>"

ADD requirements.txt requirements.txt
RUN export DEBIAN_FRONTEND=noninteractive && \ 
  apt-get update && \
  apt-get install -y python3 \
  python3-pip \
  texlive-latex-base \
  texlive-fonts-recommended \
  texlive-latex-extra \
  curl  \
  pandoc  && \
  pip install --no-cache-dir -U pip && \
  pip install --no-cache-dir -r requirements.txt && \
  pip install --no-cache-dir -U chaostoolkit chaostoolkit-reporting && \
  apt autoremove && \
  apt autoclean && \
  rm -rf /var/lib/apt/lists/* /var/cache/apt/* 

ENV MPLCONFIGDIR=/tmp/result/
VOLUME /tmp/result
WORKDIR /tmp/result

ENTRYPOINT ["/usr/local/bin/chaos"]
CMD ["report", "--export-format=pdf", "/tmp/result/journal.json", "/tmp/result/report.pdf"]
