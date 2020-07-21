FROM alpine:latest

RUN apk add --no-cache python3 py3-pip py3-gunicorn py3-aiohttp openssl
RUN pip install --no-cache-dir hpfeeds

ADD filesystem /
RUN chmod +x /docker-entrypoint.sh
WORKDIR /opt/honeypot

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["tail", "-f", "/dev/null"]
