FROM python:3.6-jessie

LABEL maintainer="chaostoolkit <contact@chaostoolkit.org>"

ADD requirements.txt requirements.txt
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y texlive-latex-base \
      texlive-fonts-recommended \
      texlive-latex-extra \
      curl && \
    curl -Lsf -o pandoc.deb https://github.com/jgm/pandoc/releases/download/2.2.1/pandoc-2.2.1-1-amd64.deb && \
    dpkg -i pandoc.deb && \
    rm -f pandoc.deb && \
    pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -U chaostoolkit chaostoolkit-reporting && \
    apt-get remove -y curl \
      texlive-latex-extra-doc \
      texlive-latex-recommended-doc \
      texlive-latex-base-doc \
      texlive-fonts-recommended-doc \
      texlive-pstricks-doc \
      texlive-pictures-doc && \
    apt-get autoremove && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

VOLUME /tmp/result
WORKDIR /tmp/result

ENTRYPOINT ["/usr/local/bin/chaos"]
CMD ["report", "--export-format=pdf", "/tmp/result/journal.json", "/tmp/result/report.pdf"]
