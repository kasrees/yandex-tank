#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

def make_ammo(method, url, headers, case, body):
    """ makes phantom ammo """
    # http request w/o entity body template
    req_template = (
        "%s %s HTTP/1.1\r\n"
        "%s\r\n"
        "\r\n"
    )

    # http request with entity body template
    req_template_w_entity_body = (
        "%s %s HTTP/1.1\n"
        "%s\n"
        "Content-Length: %d\n"
        "\n"
        "%s\n"
    )

    if not body:
        req = req_template % (method, url, headers)
    else:
        req = req_template_w_entity_body % (method, url, headers, len(body), body)

    # phantom ammo template
    ammo_template = (
        "%d %s\n"
        "%s"
    )

    return ammo_template % (len(req), case, req)

def main():
    for stdin_line in sys.stdin:
        try:
            method, url, case, body = stdin_line.split("||")
            body = body.strip()
        except:
            method, url, case = stdin_line.split("||")
            body = None

        method, url, case = method.strip(), url.strip(), case.strip()

        headers = "Host: localhost:5000\r\n" + \
                  "User-Agent: tank\r\n" + \
                  "Accept: */*\r\n" + \
                  "Content-Type: application/json\r\n" + \
                  "Connection: keep-alive\r\n" + \
                  "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ6clBzZXhPZGdGeE0xU3VaaFFZSGduWno5MXRiVktzcHdlWHRzU2VJSW1jIn0.eyJleHAiOjE3MjAxODE1NzcsImlhdCI6MTcyMDE4MDY3NywianRpIjoiODc5NzU2MjItMjczMC00YzczLWJkNzMtMTA2ZTk1ZTM0NTdkIiwiaXNzIjoiaHR0cHM6Ly9wYXJ0bmVyLnFhdGwucnUvYXV0aC9yZWFsbXMvUGFydG5lckFwaSIsImF1ZCI6IlRyYXZlbExpbmUuUGFydG5lckFQSSIsInN1YiI6IjViODljZWEzLTU3MTktNDZjMC1iYzU5LTcyZTUzYzA5YTc2MiIsInR5cCI6IkJlYXJlciIsImF6cCI6ImJyb25pX3RyYXZlbCIsInNjb3BlIjoiIiwiYXBpX2FjY2Vzc2VzIjpbInJlc2VydmF0aW9uX2FwaSIsImNvbnRlbnQiXX0.j5lscs4IJCwEQ_y2w8tgJpr7T5vf9xtnCKJQMAuSNijC4r2My3HOdEFyNBg-9qBgXpJWqzNveyd3sh-Gbevb6mpBh_d03gilaRlNuWdFmE--KeRhOIXYGhI5Q6LjYF8OGJF6eqegLLRl0DihF0mLWE5rmJcvtChLKugwRsEQHDQQu7cYo4UluuMmhGeiQT6UbKn9l2KaIkmRwm1oURIjy-WQbm-z5HRl45j5iBQFExT10DaKjcHKf9d08tXVtFaaiUOl_ilHyrzgnOdc8i0i_QdI4Qw7SCR6RIAVM7KYS7efB6kcT9ymcHGKhVrBOtUxse_tgERg8CLS6KONJhxnRA\r\n"

        sys.stdout.write(make_ammo(method, url, headers, case, body))

if __name__ == "__main__":
    main()
