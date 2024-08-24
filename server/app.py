from flask import Flask, make_response, jsonify, request
from flask_restful import Api, Resource
from flask_cors import CORS
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Instantiate REST API
api = Api(app)

# Instantiate CORS
CORS(app)

load_dotenv()

URL = os.getenv("URL")
KEY = os.getenv("KEY")
DATA_BASE_NAME = os.getenv("DATA_BASE_NAME")
CONTAINER_NAME_CLEANED = os.getenv("CONTAINER_NAME_CLEANED")

client = CosmosClient(URL, credential=KEY)
database = client.get_database_client(DATA_BASE_NAME)
COSMOSDB_CONTAINER_CASES_CLEANED = database.get_container_client(CONTAINER_NAME_CLEANED)

def get_cases_with_highest_version(cases):
    unique_cases = {}
    for case in cases:
        # Can we assume every cases have its case number?
        # Version is a string type. Will the version be assigned in lexicographic order?
        cur_case = unique_cases.get(case.get('case_number'))
        if cur_case == None or cur_case.get('version') == None or \
            case.get('version') == None or case.get('version') > cur_case.get('version'):
            unique_cases[case.get('case_number')] = case

    return unique_cases

@app.route('/')
def index():
    return '<h1>Project Server</h1>'

class Cases(Resource):
    def get(self):
        try: 
            cases = list(COSMOSDB_CONTAINER_CASES_CLEANED.read_all_items())
        except Exception as e:
            print(f"Error querying cases-cleaned database: {e.status_code} - {e.message}")
            return make_response({
                'status code': f'{e.status_code}',
                'message': f'{e.message}',
            }, 500)
        
        unique_cases = get_cases_with_highest_version(cases)
        return make_response(list(unique_cases.values()), 200)

class Case_by_case_num(Resource):
    def get(self, case_num):
        try:
            query = f"SELECT * FROM c WHERE c.case_number = '{case_num}'"
            cases = list(COSMOSDB_CONTAINER_CASES_CLEANED.query_items(query=query,enable_cross_partition_query=True))
        except Exception as e:
            print(f"Error querying cases-cleaned database: {e.status_code} - {e.message}")
            return make_response({
                'status code': f'{e.status_code}',
                'message': f'{e.message}',
            }, 500)
        
        unique_cases = get_cases_with_highest_version(cases)
        return make_response(unique_cases.get(case_num), 200)

# Fetch URL: http://localhost:5555/cases/period?startDate=2020-01-05&endDate=2021-01-04
class Cases_by_period(Resource):
    def get(self):
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        print(f'start date: {start_date}, end date: {end_date}')

        try: 
            query = f"""
                SELECT * 
                FROM c 
                WHERE c.earliest_charge_date >= '{start_date}' and c.earliest_charge_date <= '{end_date}'
                ORDER BY c.earliest_charge_date ASC
                """
            cases = list(COSMOSDB_CONTAINER_CASES_CLEANED.query_items(query=query,enable_cross_partition_query=True))
        except Exception as e:
            print(f"Error querying cases-cleaned database: {e.status_code} - {e.message}")
            return make_response({
                'status code': f'{e.status_code}',
                'message': f'{e.message}',
            }, 500)

        unique_cases = get_cases_with_highest_version(cases)
        return make_response(list(unique_cases.values()), 200)

api.add_resource(Cases, '/cases')
api.add_resource(Case_by_case_num, '/cases/<string:case_num>')
api.add_resource(Cases_by_period, '/cases/period')


if __name__ == '__main__':
    app.run(port=5555, debug=True)