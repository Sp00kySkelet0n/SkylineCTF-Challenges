FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev socat && \
    rm -rf /var/lib/apt/lists/*

COPY src/vuln.c /tmp/vuln.c
RUN mkdir -p /challenge && \
    gcc -o /challenge/vuln /tmp/vuln.c \
    -fno-stack-protector \
    -no-pie \
    -z execstack \
    -w && \
    rm /tmp/vuln.c

COPY src/flag.txt /flag.txt
RUN chmod 555 /challenge/vuln && chmod 444 /flag.txt

RUN useradd -m ctf
USER ctf

EXPOSE 9000

CMD ["socat", "TCP-LISTEN:9000,reuseaddr,fork", "EXEC:/challenge/vuln"]
