import sys
from ishare_ep import make_ep_token, create_spor_token, post_party_token
from ishare_token import create_assertion
import argparse
from ishare_sat import satellite_auth, get_party
import json


def load_entitled_party_file(file_path: str) -> dict | None:
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file: {file_path}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Process iSHARE credentials')
    parser.add_argument('--cert', required=True, help='Path to certificate file (.p12)')
    parser.add_argument('--password', required=True, help='Certificate password')
    parser.add_argument('--client-id', help='Optional client ID (defaults to certificate serial number)')
    parser.add_argument('--satellite-eori', required=True, help='iSHARE satellite URL')
    parser.add_argument('--entitled-party-file', required=True, help='Path to entitled party file')
    parser.add_argument('--satellite-url', default='https://satellite-mw.dev.dexes.eu', help='iSHARE satellite URL')
    args = parser.parse_args()

    entitled_party = load_entitled_party_file(args.entitled_party_file)
    if entitled_party is None:
        sys.exit(1)

    entitled_party_id = entitled_party["party_id"]

    assertion, serial_nr, certs, priv_key = create_assertion(
        args.cert,
        args.password,
        args.satellite_eori,
        args.client_id
    )

    if args.client_id is None:
        args.client_id = serial_nr


    print(f"serial_nr: {serial_nr}")

    satellite_url = args.satellite_url

    access_token = satellite_auth(
        satellite_url=satellite_url,
        assertion=assertion,
        client_id=args.client_id
    )

    party_info = get_party(satellite_url=satellite_url,
                      access_token=access_token,
                      party_id=entitled_party_id)
    
    # in python, empty dicts evaluate to False.
    if bool(party_info) != False:
        print(f"Party with id {entitled_party_id} exists already")
        sys.exit(1)


    print(f"Create Entitled party: {entitled_party_id}")

    spor_token = create_spor_token(
        satellite_eori=serial_nr,
        party_id=entitled_party_id,
        party_name=entitled_party["party_name"],
        capability_url=entitled_party["capability_url"],
        priv_key=priv_key,
        certs=certs
    )

    print(f"Spor token: {spor_token}")
    sys.exit(1)

    entitled_party["spor"] = {
        "signed_request": spor_token,
    }
    entitled_party["registrar_id"] = serial_nr

    ep_token = make_ep_token(
        client_id=args.client_id,
        target_id=args.satellite_eori,
        certs=certs,
        priv_key=priv_key,
        ep=entitled_party
    )

    print(f"EP token: {ep_token}")

    if not post_party_token(satellite_url=satellite_url,
                            access_token=access_token,
                            party_token=ep_token):
        print("Failed to create entitled party")
        sys.exit(1)

if __name__ == "__main__":
    main()
