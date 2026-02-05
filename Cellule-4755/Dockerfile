FROM ubuntu:20.04
RUN apt-get update && \
    apt-get install -y openssh-server sudo gcc && \
    rm -rf /var/lib/apt/lists/*
RUN useradd -m -s /bin/bash user && \
    echo "user:spongebob" | chpasswd
COPY src/vulnerable_binary.c /tmp/
RUN gcc /tmp/vulnerable_binary.c -o /usr/local/bin/vulnerable && \
    chmod 4755 /usr/local/bin/vulnerable
COPY src/entrypoint.sh /entrypoint.sh

COPY src/flag.txt /root/flag.txt

RUN chmod +x /entrypoint.sh && \
    chmod 600 /root/flag.txt

RUN mkdir -p /run/sshd && \
    sed -i 's|#PermitRootLogin prohibit-password|PermitRootLogin no|' /etc/ssh/sshd_config && \
    sed -i 's|#PasswordAuthentication yes|PasswordAuthentication yes|' /etc/ssh/sshd_config
EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]

