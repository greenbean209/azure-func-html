from lib2to3.pytree import convert
import logging
from multiprocessing import reduction

import azure.functions as func

import pandas_datareader.data as web        
from datetime import datetime


def convert_date(date):
    input_date = date
    slash_date = input_date.replace('-','/')
    date_format = '%Y/%m/%d'
    converted_date = datetime.strptime(slash_date, date_format)
    return converted_date

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('Python HTTP trigger function processed a request.')

    # Get request parameters
    start = req.params.get('start')
    end = req.params.get('end')

    logging.info(start)
    logging.info(end)

    # If start and end params are defined execute query
    if (start and end):

        # Convert incoming date in yyyy-mm-dd format to datetime
        start_datetime = convert_date(start)
        end_datetime = convert_date(end)

        # Query FRED for gas prices
        gas_prices = web.DataReader('APUS37B74714', 'fred', start_datetime, end_datetime)
        print(gas_prices.info())
        gas_prices.reset_index(inplace=True)

        # Convert df to html
        table_html=gas_prices.to_html(classes="query_table")
        
        # Define HTML Template 123
        template_html = '''
        <!DOCTYPE html>
        <html>
            <head>
                    <style>
                    .query_table {{
                    font-size: 11pt; 
                    font-family: Arial;
                    border-collapse: collapse; 
                    border: 1px solid silver;
                    }}

                    .query_table td, th {{
                        padding-top: 5px;
                        padding-bottom: 5px;
                        padding-left: 10px;
                        padding-right: 10px;
                        text-align: center;
                    }}

                    .query_table tr:nth-child(even) {{
                        background: #E0E0E0;
                    }}

                    .query_table tr:hover {{
                        background: silver;
                        cursor: pointer;
                    }}
                </style>
                <title>HTML Pandas Dataframe with CSS</title>
            </head>
        <body>
            {table}
        </body>
        </html>
        '''

        # Format to produce repsonse html
        response_html = template_html.format(table=table_html)

        # Retunr http response
        return func.HttpResponse(
             status_code=200,
             headers={'content-type':'text/html'},
             body=response_html
        )
    else:
        # if start and end are not defined, indicate invalid date range
        return func.HttpResponse(
             status_code=200,
             headers={'content-type':'text/html'},
             body='Invalid query date range'
        )

