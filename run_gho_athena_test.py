from dotenv import load_dotenv
from gho_api import fetch_gho_indicators_for_pakistan
from athena_api import sync_athena_to_postgresql
import os

load_dotenv()

print('Running GHO sync...')
result = fetch_gho_indicators_for_pakistan()
print('GHO result:', result)

print('Running Athena sync...')
aws_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
athena_result = sync_athena_to_postgresql(aws_key, aws_secret)
print('Athena result:', athena_result)
