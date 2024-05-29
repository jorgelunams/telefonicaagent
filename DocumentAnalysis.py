"""
This code sample shows Prebuilt Read operations with the Azure Form Recognizer client library. 
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Document Intelligence (formerly Form Recognizer) SDKs
https://learn.microsoft.com/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?pivots=programming-language-python
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

 
from dotenv import load_dotenv
import os
load_dotenv()

# Get the connection string
endpoint = os.getenv('DOCUMENT_ENDPOINT')
key = os.getenv('DOCUMENT_KEY')

"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""
 

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

def analyze_read(FileURL):
    # sample document
    
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    
    poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-read", FileURL)
    result = poller.result() 

    pages_content = []  # List to hold the content of each page
    for page in result.pages: 
        content_string = ""  # Initialize content_string for each page
        for line_idx, line in enumerate(page.lines): 
           content_string += line.content + " "
        pages_content.append(content_string)  # Add the content of the page to the list

    return pages_content