# Indigent_stats_backend

This is a back-end application to provide with APIs to access public case records from the Azure Cosmos DB, indigent-defense-stats-prod-cosmos-acct.

## Install

1. Clone this repo and navigate to it.
   - `git clone https://github.com/kjbyun0/indigent-stats-backend`
   - `cd indigent-stats-backend`
2. Run pipenv install to build a virtual environemnt
   - `pipenv install`
3. Run the virtual environment
   - `pipenv shell`
4. Run app.py
   - `cd server`
   - `python app.py`

## APIs

There are following three APIs available at the moment. 

1. An API to access all cases
   - `http://localhost:5555/cases`

2. An API to access a case by case number
   - `http://localhost:5555/case/${case_number}`

3. An API to access cases which falls in the given time period
   - `http://localhost:5555/cases/period?startDate=${startDate}&endDate=${endDate}`