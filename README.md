# EP Creation tool

Example usage.

1st. Create a JSON file describing the EP (see `eps/argaelo.json` for an example)

2nd. Run the script

```bash
uv run main.py \
    --cert $CERT_P12 \
    --password $CERT_P12_PASSWORD \
    --entitled-party-file $FILE_PATH
```
