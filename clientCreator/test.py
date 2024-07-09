text = "GET /resources/available-properties HTTP/1.1\n" + \
"Host: localhost:5000\n" + \
       "User-Agent: tank\n" + \
       "Accept: */*\n" + \
       "Content-Type: application/json\n" + \
       "Connection: keep-alive\n" + \
       "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ6clBzZXhPZGdGeE0xU3VaaFFZSGduWno5MXRiVktzcHdlWHRzU2VJSW1jIn0.eyJleHAiOjE3MjAxODI4MzAsImlhdCI6MTcyMDE4MTkzMCwianRpIjoiMzE3YmMzZGUtNjgzMC00OGU4LTgyZjEtMTliMWZlNDE0MWMwIiwiaXNzIjoiaHR0cHM6Ly9wYXJ0bmVyLnFhdGwucnUvYXV0aC9yZWFsbXMvUGFydG5lckFwaSIsImF1ZCI6IlRyYXZlbExpbmUuUGFydG5lckFQSSIsInN1YiI6ImM3NmUxNDA0LTQ0MGUtNDdjOS1iMGU1LTIzYWFiOTg2MTk0ZCIsInR5cCI6IkJlYXJlciIsImF6cCI6ImxvYWRfdGVzdF9wYXJ0bmVyXzEiLCJzY29wZSI6IiIsImFwaV9hY2Nlc3NlcyI6WyJjb250ZW50Il19.JyU5GOkH9PCkqIP1I53W-r2JAkqV--74d4EMmPdOEyoJCamkwafsfYEXw8h0FxedYA9woDkc2y9teiGeXmQGJDXULIYAaZyWEiz-epQ8zmzhKgQxYS3PxeYRuUbu9lgztZJXcEDffcNL1W604wGtbILFI4ujtmAWrYVA-i9WqYbog9VPUU-bDe3YTZ7zFgNR4GVGdGN3EKmdVahmitht6Qck4rpjPAjcsBgUveSaDfmcF9etG8PlGxw4NfNJrhjt9IclChh6iE3-JI95pgNtKw5_XZJo4I--kJ0i9smHneHZl3JX7oJ3Pc-PGzWUp1tzW_BQdsw7DYxWDDBn441ulA" + \
       "\r\n"


with open('../loadtest/ammo.txt', 'w') as f:
    f.write(text)

print(len(text))