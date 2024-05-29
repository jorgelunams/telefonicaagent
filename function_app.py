import azure.functions as func
import logging

import OpenAIKernel as oai

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS) 
@app.route(route="TelcelAgent")
async def TelcelAgent(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    query = req.params.get('query')
    if not query:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            query = req_body.get('query')

    if query:
        response = await oai.semantic_agent(query)
        return func.HttpResponse(f"Response: {response}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a query in the query string or in the request body for a personalized response.",
             status_code=200
        )