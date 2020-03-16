#!/opt/bin/python3

import http.client, urllib

def send_message(title, message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": "agixw6imtgs59zigj2mmzfspajstun",
            "user": "u8rfcaghrikib2i4qtkkazoqc4m9dd",
            "title": title
            "message": message,
        }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
