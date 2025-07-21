# Entitled Party Creation Tool

This tool facilitates the creation of Entitled Parties (EPs) within the iSHARE ecosystem. It automates the process of registering new parties on an iSHARE satellite, handling all the required authentication, token generation, and API communication.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Create an Entitled Party JSON File](#create-an-entitled-party-json-file)
  - [Running the Tool](#running-the-tool)
  - [Command-Line Arguments](#command-line-arguments)
- [File Structure](#file-structure)
- [Technical Details](#technical-details)
  - [Authentication Flow](#authentication-flow)
  - [Token Generation](#token-generation)
- [Example JSON Format](#example-json-format)
- [Generate Entitled Party JSON Files from CSV](#generate-entitled-party-json-files-from-csv)
- [Troubleshooting](#troubleshooting)

## Overview

The Entitled Party Creation Tool interacts with the iSHARE satellite to register new parties. It handles:

- Authentication with the iSHARE satellite using certificate-based client assertions
- Generation of SPOR (Signed Party Object Request) tokens
- Creation and submission of Entitled Party data
- Verification of party existence to prevent duplicates

## Requirements

- Python 3.12 or higher
- Valid iSHARE Satellite certificate (.p12 format) with appropriate permissions
- Appropriate permissions on the iSHARE satellite

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd entitled-party
```

2. Install uv if you don't have it already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install the dependencies using uv:

```bash
uv sync
```

## Usage

### Create an Entitled Party JSON File

First, create a JSON file describing the Entitled Party. See the [Example JSON Format](#example-json-format) section or check the provided `eps/argaelo.json` file as a template.

### Running the Tool

Execute the main script with your certificate and entitled party file:

```bash
uv run main.py \
    --cert /path/to/your/certificate.p12 \
    --password YOUR_CERT_PASSWORD \
    --entitled-party-file eps/your_ep.json \
    --satellite-url https://satellite-mw.the.domain.org
```

### Command-Line Arguments

The script accepts the following arguments:

- `--cert`: Path to your .p12 certificate file (required)
- `--password`: Password for the certificate (required)
- `--entitled-party-file`: Path to the JSON file describing the entitled party (required)
- `--satellite-url`: iSHARE Satellite middleware URL (required)
- `--client-id`: Optional override of client ID (defaults to certificate serial number)

## File Structure

- `main.py`: Entry point of the application
- `ishare_token.py`: Handles JWT token generation and certificate parsing
- `ishare_ep.py`: Functions for creating and posting Entitled Party data
- `ishare_sat.py`: Functions for satellite authentication and querying
- `eps/`: Directory containing example Entitled Party JSON files

## Technical Details

### Authentication Flow

1. The tool extracts certificates and private keys from the provided .p12 file
2. It creates a JWT client assertion for authentication
3. The assertion is used to obtain an access token from the satellite
4. The access token is then used for subsequent API calls

### Token Generation

The tool generates two primary types of tokens:
- **SPOR Token**: A base64-encoded JWT containing party identification information
- **EP Token**: A JWT containing full entitled party details

Both tokens are cryptographically signed using the private key from the provided certificate.

## Example JSON Format

The entitled party JSON file must follow this structure:

```json
{
    "party_id": "YOUR.EORI.IDENTIFIER",
    "party_name": "Your Company Name",
    "capability_url": "",
    "registrar_id": null,
    "adherence": {
        "status": "Active",
        "start_date": "YYYY-MM-DDT00:00:00.000Z",
        "end_date": "YYYY-MM-DDT00:00:00.000Z"
    },
    "additional_info": {
        "description": "",
        "logo": "",
        "website": "",
        "company_phone": "",
        "company_email": "",
        "publicly_publishable": "false",
        "countriesOfOperation": [],
        "sectorIndustry": [],
        "tags": ""
    },
    "agreements": [
        {
            "type": "TermsOfUse",
            "title": "ToU",
            "status": "Accepted",
            "sign_date": "YYYY-MM-DDT00:00:00.000Z",
            "expiry_date": "YYYY-MM-DDT00:00:00.000Z",
            "agreement_file": "file_identifier",
            "framework": "iSHARE",
            "dataspace_id": "DATASPACE.ID",
            "dataspace_title": "Dataspace Title",
            "complaiancy_verified": "yes"
        }
    ],
    "certificates": [],
    "roles": [
        {
            "role": "EntitledParty",
            "start_date": "YYYY-MM-DDT00:00:00.000Z",
            "end_date": "YYYY-MM-DDT00:00:00.000Z",
            "loa": "Low",
            "complaiancy_verified": "yes",
            "legal_adherence": "yes"
        }
    ],
    "authregistery": []
}
```

## Generate Entitled Party JSON Files from CSV

You can generate multiple entitled party JSON files from a CSV file using the provided [transformation script](./transform_csv_to_json.py). This is useful when onboarding many parties at once.

### Input CSV Format

The CSV file must contain the following **semicolon-separated** fields:
party_id;party_name;start_date;end_date;description;logo;website;company_phone;company_email;ToU_sign_date;ToU_expiry_date;ToU_agreement_file;AA_sign_date;AA_expiry_date;AA_agreement_file

The fields party_id, party_name start_date and end_date are required. The rest of the fields will be defaulted to an empty string if they are left empty.

### Template File

The script requires a base JSON template that contains default values for fields not provided in the CSV. This template is merged with each CSV row to create a complete entitled party JSON document. A base template is provider in [template.json](./template.json).

### Example usage

```
transform_csv_to_json.py \
    --template-file template.json \
    --ep-csv entitled_parties.csv \
```

This command will:
	1.	Read entitled_parties.csv
	2.	Merge each row with template.json
	3.	Write one JSON file per party into the eps directory

Each resulting file will be named like <row-index>_<party-id>.json.

## Troubleshooting

- **Certificate Issues**: Ensure your .p12 certificate is valid and the password is correct
- **Party Already Exists**: The tool will check if a party with the given ID already exists and exit if it does
- **API Response Errors**: Check the console output for detailed error messages from the satellite
- **JSON Format Issues**: Ensure your entitled party JSON file follows the required structure
