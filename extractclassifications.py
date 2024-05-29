# Import necessary modules
import asyncio
import Gen2Services as g2s
import searchaiservice as search
import DocumentAnalysis as da 
import OpenAIKernel as oai
import json
from dotenv import load_dotenv
import os
load_dotenv() 
import Tools as tools 
import asyncio
import classify_questions as clas  # replace with the name of the module that contains the extract_problema_column function
import sys
print(sys.path)
# Get the connection string
connection_string = os.getenv('CONNECTION_STRING')
async def extract_problems():
    problema_column =  await clas.extract_problema_column('C:\\Data\\Telefonica\\prob_sol.csv')  
    print(problema_column)
    
def merge():
    clas.merge_files("telefonicadata/KBDEV/ProblemasSoluciones", "TransformedQA", 2900)

   
def summary_category():
    clas.SummaryCategory()
  
def group_summary():
    clas.GroupSummary()  
  
def create_index_manual_solutions():
    search.create_search_index_manual_solutions("manual_solutions_index") 
  
def create_index_manual_roaming_solutions():
    search.create_search_index_manual_roaming_solutions("manual_roaming_solutions_chunking_index")
    
async def testOpenAI():
    await oai.TestOpenAI()
 

def insert_manual():
    search.insert_manual_with_embeddings("manual_solutions_index")


def insert_roaming_manual():
    search.insert_manual_roaming_with_embeddings("manual_roaming_solutions_index") 


def insert_roaming_chunking_manual():
    search. insert_manual_roaming_chunking_with_embeddings("manual_roaming_solutions_chunking_index")
       
    
def insert_documents():
    search.insert_document("manual_index")
    


def vector_search():
    search.VectorQASearch("manual_index", "mi red esta caida ntengo coneccion")

def vector_search_manual():
    search.VectorManualSolutionsSearch("manual_solutions_index", "mi red esta caida no tengo conexion al internet")
   
async def telefonica_agent():
    await oai.semantic_agent()
      
   
async def telefonica_ai_agent():
    await oai.telefonica_ai_agent("Que es Pasaporte RRS y caundo expira?")
    

   
async def get_intent():
    await oai.get_intent("Que es Pasaporte RRS y caundo expira?", "Hay roaming en Argentina")


async def semantic_ai_agent():
    await oai.semantic_agent("Que es Pasaporte RRS y caundo expira??")


   


   

##FileName = "ProblemasFuncionamiento"
FileName = "RoamingPages110"
# Function to get the URL of the file from Azure Data Lake Gen2
async def use_gen2_services():     
    url = g2s.get_file_url(connection_string, "telefonicadata/KBDEV/ManualsDocuments",  FileName + ".pdf")
    return url

 
async def ExtractQA():
    fileURL = await use_gen2_services()
    
    # Analyze the document content
    documentContent = da.analyze_read(fileURL)
    totalTokens = tools.num_tokens_from_string(documentContent, "cl100k_base") 
    documentContent = documentContent.replace("&", " and ")
    
    ##Results2 = await oai.analyze_document_problems(documentContent, totalTokens) 
    
    ##data = json.loads(Results2) 
    ##json_data_Problem = json.dumps(data)
    # Upload the JSON string to the DataLake
   ## g2s.upload_to_datalake(connection_string, "telefonicadata/KBDEV/ManualsDocuments", "MovistartCLProblems" + ".json", json_data_Problem) 
    
    Results1 = await oai.analyze_document_QA(documentContent, totalTokens)
    data = json.loads(Results1.replace('\n', ''))

    # Convert the Results1 object to a JSON string and remove newline characters
    json_data_QA = json.dumps(data, ensure_ascii=False).replace('\n', '') 

    with open('C:/Data/Telefonica/ProblemasFUncionamientoQA.json', 'w', encoding='utf-8') as f:
        f.write(json_data_QA)
    
    g2s.upload_to_datalake(connection_string, "telefonicadata/KBDEV/ManualsDocuments", "ProblemasFuncionamientoQA" + ".json", json_data_QA)
   
    ##QA = str(Results2)
    ##totalTokens = tools.num_tokens_from_string(QA, "cl100k_base")


### Old version to extract data from all pages in one shot 
async def ExtractManualProblems():
    fileURL = await use_gen2_services()
    
    # Analyze the document content
    documentContent = da.analyze_read(fileURL)
    documentPages = ' '.join(documentContent)  # Combine all pages into a single string
    totalTokens = tools.num_tokens_from_string(documentPages, "cl100k_base")
    
    ##Results2 = await oai.analyze_document_problems(documentContent, totalTokens) 
    
    ##data = json.loads(Results2) 
    ##json_data_Problem = json.dumps(data)
    # Upload the JSON string to the DataLake
   ## g2s.upload_to_datalake(connection_string, "telefonicadata/KBDEV/ManualsDocuments", "MovistartCLProblems" + ".json", json_data_Problem) 
    
    Results1 = await oai.analyze_document_problems(documentPages, totalTokens)
    data = json.loads(Results1.replace('\n', ''))
    
    text_pages = []
    
    # Assuming data is a list of dictionaries and documentContent is a list of page contents
        # Assuming data is a list of dictionaries and documentContent is a list of page contents
    for record in data:
    # Extract pages and split by comma or dash, then convert to list of integers
        pages = [int(page) for page_range in record.get('paginas', '').split(',') for page in page_range.split('-')]  
        # Get the corresponding page contents from documentContent and join them into a single string
        record['texto_paginas'] = ' '.join([documentContent[page - 1] for page in pages if page - 1 < len(documentContent)])
    # Add text_pages to each record in data
        # Assuming data is a list of dictionaries
    for record in data:
        # Extract pages and split by comma, then convert to list of integers 
        record['problema'] += ' Titulo: ' + record.get('titulo', '') + ', Subtitulo: ' + record.get('subtitulo', '') + ', Nombre Opcion: ' + record.get('nombre_opcion', '')
        
    json_data_QA = json.dumps(data, ensure_ascii=False).replace('\n', '') 

    
    with open('C:/Data/Telefonica/RoamingPage100PR.json', 'w', encoding='utf-8') as f:
        f.write(json_data_QA)
    
    g2s.upload_to_datalake(connection_string, "telefonicadata/KBDEV/ManualsDocuments", "RoamingPage100PR" + ".json", json_data_QA)
    
### New code to extract data from each page in the document
### This code will extract data from each page in the document and upload the results to the DataLake
### The code will also concatenate the values of 'titulo', 'subtitulo', and 'nombre_opcion' to 'problema'
async def ExtractManualRoamingProblems():
    fileURL = await use_gen2_services()
        
    import re
    # Analyze the document content
    documentContent = da.analyze_read(fileURL)
    # Combine all lines into a single string
    documentPages = ' '.join(documentContent)
    # Split the document into pages based on delimiter  
    pages = re.split('\*+', documentPages)
    # Remove leading/trailing white space from each page
    pages = [page.strip() for page in pages]
    totalTokens = tools.num_tokens_from_string(documentPages, "cl100k_base")
    # Remove the last page if it's empty
    if not pages[-1]:  
        pages.pop() 
    
    totalTokens = [tools.num_tokens_from_string(page, "cl100k_base") for page in pages]  
    ##Results2 = await oai.analyze_document_problems(documentContent, totalTokens) 
    
    ##data = json.loads(Results2) 
    ##json_data_Problem = json.dumps(data)
    # Upload the JSON string to the DataLake
   ## g2s.upload_to_datalake(connection_string, "telefonicadata/KBDEV/ManualsDocuments", "MovistartCLProblems" + ".json", json_data_Problem) 
    a = 1   
    analysis_results = []   
    for page, tokens in zip(pages, totalTokens):  
            try:
                # Skip processing if page is empty or contains only spaces
                if not page.strip():
                    continue
                # Analyze the current page  
                result = await oai.analyze_document_problems(page, "roaming_page60", a)  
                # Parse the result and add to the list of results  
                analysis_results.append(json.loads(result.replace('\n', '')))  
                a += 1  

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
 
    
    # Convert each dictionary in analysis_results to a string before joining them
    data = [json.loads(item.replace('\n', '')) for item in map(json.dumps, analysis_results)]

    
    for record in data:
    # Access the dictionary in record
        dict_record = record[0]
        # Concatenate the values of 'titulo', 'subtitulo', and 'nombre_opcion' to 'problema'
        dict_record['problema'] = str(dict_record.get('problema', '')) + ' Titulo: ' + str(dict_record.get('titulo', '')) + ', Subtitulo: ' + str(dict_record.get('subtitulo', '')) + ', Nombre Opcion: ' + str(dict_record.get('nombre_opcion', ''))
    
    json_data_QA = json.dumps(data, ensure_ascii=False).replace('\n', '') 

    
    with open('C:/Data/Telefonica/RoamingPage60PR.json', 'w', encoding='utf-8') as f:
        f.write(json_data_QA)
    
    g2s.upload_to_datalake(connection_string, "telefonicadata/KBDEV/ManualsDocuments", "RoamingPage60PR" + ".json", json_data_QA)
   
   
async def ExtractSolutionManual():
    connection_string = os.getenv('CONNECTION_STRING')
    file_data = g2s.download_content_as_json(connection_string, "telefonicadata", "KBDEV/Silver/preguntas_sample.json")
    manualAcademia = g2s.download_content_as_json(connection_string, "telefonicadata", "KnowledgeBase/Manuals/MovistartCL.json")
    # Count the categories
    manualAcademia_json = json.dumps(manualAcademia)
    
    ##filtered_data = [item for item in file_data if item['category'] == "Preguntas sobre equipos 5G"]
    
    # Filter the data again to only include items with 'clasificacion' as 'ProblemaTecnico'
    filtered_data = [item for item in file_data if item['clasificacion'] == "ProblemaTecnico"]
    
    problema_list = [item['problema'] for item in filtered_data]
    Results1 = await oai.SetSolution(problema_list, manualAcademia_json) 
    data = json.loads(Results1) 

    # Convert the Results1 object to a JSON string
    json_data_QA = json.dumps(data)

    # Upload the JSON string to the DataLake
    g2s.upload_to_datalake(connection_string, "telefonicadata/KnowledgeBase/Silver", "AdvancedSolutionMovistarCL" + ".json", json_data_QA) 
# Run the async function
##asyncio.run(ExtractManualRoamingProblems())
##asyncio.run(extract_problems())
##asyncio.run(ExtractQA())
##merge()
##summary_category()
##group_summary()
##manual_summary()
##create_embedings()
##create_index_Manual_QA()
##create_index_manual_roaming_solutions()
##insert_documents()
##insert_manual()
insert_roaming_chunking_manual()
insert_roaming_manual()
##vector_search_manual()
##telefonica_agent()
##vector_search()
##asyncio.run(ExtractManualProblems())
##asyncio.run(ExtractManualRoamingProblems())
##asyncio.run(testOpenAI())
##asyncio.run(telefonica_agent())
##asyncio.run(telefonica_ai_agent())

##asyncio.run(semantic_ai_agent()) 
##asyncio.run(get_intent())
##create_index_manual_roaming_solutions()
