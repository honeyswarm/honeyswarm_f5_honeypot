#!/bin/sh

# This is a bit odd but we are going to listen on both 443 and 8443 jsut because. . . 
# AUtomated scans unlikly to spot the difference. 

# Check to see if we are starting HTTPS as well
printf "[+] Setting up HTTPS Certs\n"
openssl req -nodes -new -x509 -days 365 -keyout ca.key -out ca-crt.pem -subj "/C=--/ST=WA/L=Seattle/O=MyCompany/OU=MyOrg/CN=localhost.localdomain/emailAddress=root@localhost.localdomain"

printf "[+] Setting listener on 443\n"
gunicorn -D -w 5 --certfile=/opt/honeypot/ca-crt.pem --keyfile=/opt/honeypot/ca.key app:app -b 0.0.0.0:443 --worker-class aiohttp.worker.GunicornWebWorker

printf "[+] Setting listener on 8443\n"
gunicorn -D -w 5 --certfile=/opt/honeypot/ca-crt.pem --keyfile=/opt/honeypot/ca.key app:app -b 0.0.0.0:8443 --worker-class aiohttp.worker.GunicornWebWorker


# Now run the CMD
exec "$@"