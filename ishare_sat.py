import requests
import urllib.parse
import jwt


def satellite_auth(
        satellite_url: str,
        client_id: str,
        assertion: str,
) -> str:
    atype = "urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer"

    payload = "&".join([
        "grant_type=client_credentials",
        f"client_assertion_type={atype}",
        f"client_id={client_id}",
        "scope=iSHARE",
        f"client_assertion={assertion}",
    ])

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.request("POST",
                                urllib.parse.urljoin(
                                    satellite_url,
                                    "/connect/token"
                                ),
                                headers=headers,
                                data=payload)

    if response.status_code != 200:
        print(f"status_code: {response.status_code}, text: {response.text}")
    response.raise_for_status()
    return response.json()["access_token"]


def satellite_get_trusted_list(
        satellite_url: str,
        access_token: str,
):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.request("GET",
                                urllib.parse.urljoin(
                                    satellite_url,
                                    "/trusted_list"
                                ),
                                headers=headers)
    response.raise_for_status()
    tk = response.json()["trusted_list_token"]

    # verify_signature true does not work
    return jwt.decode(tk, options={"verify_signature": False})


def satellite_get_parties(
        satellite_url: str,
        access_token: str,
        party_eori: str = "*",
):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    query = "&".join([
        f"eori={party_eori}",
        "active_only=true",
    ])

    response = requests.request("GET",
                                urllib.parse.urljoin(
                                    satellite_url,
                                    f"/parties?{query}"
                                ),
                                headers=headers)
    response.raise_for_status()
    tk = response.json()["parties_token"]

    # verify_signature true does not work
    return jwt.decode(tk, options={"verify_signature": False})


def get_party(
        satellite_url: str,
        access_token: str,
        party_id: str,
):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.request("GET",
                                urllib.parse.urljoin(
                                    satellite_url,
                                    f"/parties/{party_id}"
                                ),
                                headers=headers)
    response.raise_for_status()
    tk = response.json()["party_token"]

    # verify_signature true does not work
    return jwt.decode(tk, options={"verify_signature": False})["party_info"]
