FROM ubuntu:24.04

# you can overwrite this otherwise just leave it as-is as placeholder for
# pdm to be happy
ARG PDM_BUILD_SCM_VERSION=0.0.0

RUN groupadd -g 1001 svc && useradd -r -u 1001 -g svc svc
WORKDIR  /home/svc
COPY . /home/svc

RUN export DEBIAN_FRONTEND=noninteractive && \ 
  apt-get update -y && \
  apt-get install -y --no-install-recommends build-essential curl gcc texlive-latex-base texlive-fonts-recommended texlive-latex-extra pandoc && \
  apt-get install -y python3.12 python3.12-dev python3-pip python3.12-venv && \
  curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 - && \
  export PATH=/root/.local/bin:$PATH  && \
  pdm install -v --prod -G ctk --no-editable --lock /py12-linux.lock && \
  apt autoremove && \
  apt autoclean && \
  rm -rf /var/lib/apt/lists/* /var/cache/apt/* 

ENV MPLCONFIGDIR=/tmp/result/
VOLUME /tmp/result
WORKDIR /tmp/result

ENTRYPOINT ["/home/svc/.venv/bin/chaos"]
CMD ["report", "--export-format=pdf", "/tmp/result/journal.json", "/tmp/result/report.pdf"]
