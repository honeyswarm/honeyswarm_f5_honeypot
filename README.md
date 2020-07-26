### honeyswarm_f5_honeypot

Honeyswarm Honeypot for F5 BIGIP

This honeypot is configured to work with a HoneySwarm HPFeeds Broker. 

### Example Log

```
{
    "hive_id": "5ead9c89e191ce3a39c63404",
    "http_headers": {
        "Accept": "*/*",
        "Content-Length": "28",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "f5-bigip.home.lab",
        "User-Agent": "curl/7.58.0"
    },
    "http_host": "f5-bigip.home.lab",
    "http_method": "POST",
    "http_path": "/tmui/",
    "http_post": {
        "command": "list auth user admin"
    },
    "http_query": "/tmui/",
    "http_remote": "52.23.25.64",
    "http_scheme": "https",
    "http_version": "HTTP/1.1",
    "src_ip": "52.23.25.64"
}
```
