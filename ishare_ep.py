import requests
import urllib.parse
import jwt
import uuid
from datetime import datetime, timezone
from typing import Any
import base64


def create_spor_token(
        satellite_eori: str,
        party_id: str,
        party_name: str,
        capability_url: str,
        priv_key: str,
        certs: list[str]
) -> str:

    # Create payload
    payload = {
        "iss": satellite_eori,
        "sub": satellite_eori,
        "aud": satellite_eori,
        "party_id": party_id,
        "party_name": party_name,
        "capability_url": capability_url,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    }

    # Create header
    header = {
        "alg": "RS256",
        "typ": "JWT",
        "x5c": certs,
    }

    # Generate signed token
    signed_token = jwt.encode(payload, priv_key, headers=header, algorithm="RS256")
    
    # Base64 encode the signed token
    return base64.b64encode(signed_token.encode()).decode()


def make_ep_token(
        client_id: str,
        target_id: str,
        certs: list[str],
        priv_key: str,
        ep: object
) -> str:

    # Create header
    # Specifying additional header values ("x5c" & "typ"), in addition
    # to the standard value "alg"
    header: dict[str, Any] = {}
    header["typ"] = "JWT"
    header["x5c"] = certs

    now = datetime.now(timezone.utc).timestamp()
    # Create payload
    iss = client_id
    sub = client_id
    aud = target_id
    jti = str(uuid.uuid1())
    iat = int(now)
    nbf = iat
    exp = iat + 30

    payload: dict[str, Any] = {}
    payload["iss"] = iss
    payload["sub"] = sub
    payload["nbf"] = nbf
    payload["aud"] = aud
    payload["jti"] = jti
    payload["iat"] = iat
    payload["exp"] = exp
    payload["parties_info"] = ep

    # Generate client assertion
    client_assertion = jwt.encode(
        payload, priv_key, headers=header, algorithm="RS256")

    return client_assertion #client_assertion.decode('utf-8')


def post_party_token(satellite_url: str,
                     access_token: str,
                     party_token: str) -> bool:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
   
    payload = {
        "ep_creation_token": party_token
    }

    response = requests.post(urllib.parse.urljoin(satellite_url, f"/ep_creation"),
                             headers=headers,
                             json=payload)
    
    if response.status_code != 200:
        print(f"status_code: {response.status_code}, text: {response.text}")
        return False
    
    return True