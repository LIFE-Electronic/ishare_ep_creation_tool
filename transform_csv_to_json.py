import csv
import json
import argparse

required_fields = [
    "party_id",
    "party_name",
    "start_date",
    "end_date",
    "ToU_sign_date",
    "ToU_expiry_date",
    "ToU_agreement_file",
    "AA_sign_date",
    "AA_expiry_date",
    "AA_agreement_file"
]

def map_agreement(
    agreement,
    tou_sign_date,
    tou_expiry_date,
    tou_agreement_file,
    aa_sign_date,
    aa_expiry_date,
    aa_agreement_file
):
    if agreement["type"] == "TermsOfUse":
        return {
            **agreement,
            "sign_date": tou_sign_date,
            "expiry_date": tou_expiry_date,
            "agreement_file": tou_agreement_file
        }
    
    if agreement["type"] == "AccessionAgreement":
        return {
            **agreement,
            "sign_date": aa_sign_date,
            "expiry_date": aa_expiry_date,
            "agreement_file": aa_agreement_file
        }
    
    return agreement

def main():
    parser = argparse.ArgumentParser(description='Transform entitled party csv into json file format to be used in creation script')
    parser.add_argument("--template-file", required=True, help="JSON file to act as a base for all the properties that are not present in the csv")
    parser.add_argument("--ep-csv", required=True, help="CSV file containing rows of entitled parties to be created in the following format => party_id;party_name;start_date;end_date;description;logo;website;company_phone;company_email;ToU_sign_date;ToU_expiry_date;ToU_agreement_file;AA_sign_date;AA_expiry_date;AA_agreement_file")
    parser.add_argument("--output-dir", default="./eps", help="Directory to store the resulting entitled party JSON files")
    args = parser.parse_args()


    print("loading template: ", args.template_file)
    with open(args.template_file) as f:
        template = json.load(f)

    with open(args.ep_csv) as f:
        reader = csv.DictReader(f, delimiter=';')
        for idx, row  in enumerate(reader, start=1):
            missing_field = next((field for field in required_fields if not row.get(field)), None)

            if missing_field:
                print(f"{missing_field} not found for row #{idx} --- skipping row")
                continue
            
            party_id = row["party_id"]

            print("handling party: ", party_id)

            agreements = [
                map_agreement(
                    x,
                    row["ToU_sign_date"],
                    row["ToU_expiry_date"],
                    row["ToU_agreement_file"],
                    row["AA_sign_date"],
                    row["AA_expiry_date"],
                    row["AA_agreement_file"]
                )
                for x in template["agreements"]
            ]

            output = {
                **template,
                "party_id": party_id,
                "party_name": row["party_name"],
                "adherence": {
                    "status": "Active",
                    "start_date": row["start_date"],
                    "end_date": row["end_date"]
                },
                "additional_info": {
                    **template["additional_info"],
                    "description": row["description"],
                    "logo": row["logo"],
                    "website": row["website"],
                    "company_phone": row["company_phone"],
                    "company_email": row["company_email"]
                },
                "agreements": agreements
            }

            filename = f"{args.output_dir}/{idx}_{party_id}.json"
            with open(filename, "w") as f:
                print(f"writing to entitled party json file: {filename}")
                json.dump(output, f, indent=4)

if __name__ == "__main__":
    main()