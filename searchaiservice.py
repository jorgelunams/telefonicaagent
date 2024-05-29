from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv 
import Gen2Services as g2s
from azure.identity import DefaultAzureCredential 
from azure.core.credentials import AzureKeyCredential
import os
import json
from azure.search.documents import SearchClient    
from langchain.text_splitter import TokenTextSplitter
import uuid
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex
)
text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=205)  
 

def create_search_index_manual_solutions(index_name):

# Create a search index
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]) if len(os.environ["AZURE_SEARCH_API_KEY"]) > 0 else DefaultAzureCredential()
    index_client = SearchIndexClient(
    endpoint=endpoint, credential=credential)
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
        SearchableField(name="problema", type=SearchFieldDataType.String),
        SearchableField(name="tipo_problema", type=SearchFieldDataType.String),  
        SearchableField(name="soluciones", type=SearchFieldDataType.String),  
        SearchableField(name="paginas", type=SearchFieldDataType.String),  
        SearchableField(name="nombre_manual", type=SearchFieldDataType.String),    
        SearchableField(name="titulo", type=SearchFieldDataType.String),  
        SearchableField(name="subtitulo", type=SearchFieldDataType.String),
        SearchableField(name="nombre_opcion", type=SearchFieldDataType.String),
        SearchableField(name="texto_paginas", type=SearchFieldDataType.String), 
        
        SearchField(name="problemaVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
        SearchField(name="solucionesVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),  
       
        
]
    
    # Configure the vector search configuration  
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            )
        ]
    ) 
    semantic_config = SemanticConfiguration(
    name="manual-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="paginas"),
        content_field=SemanticField(field_name="pregunta")       
        )
    )
    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index with the semantic settings
    index = SearchIndex(name=index_name, fields=fields,
                        vector_search=vector_search, semantic_search=semantic_search)
    result = index_client.create_or_update_index(index)
    print(f' {result.name} created') 
    

def create_search_index_manual_roaming_solutions(index_name):

# Create a search index
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]) if len(os.environ["AZURE_SEARCH_API_KEY"]) > 0 else DefaultAzureCredential()
    index_client = SearchIndexClient(
    endpoint=endpoint, credential=credential)
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
        SearchableField(name="problema", type=SearchFieldDataType.String),
        SearchField(name="chunk_id", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=False, searchable=False),
        SearchableField(name="tipo_problema", type=SearchFieldDataType.String, sortable=False, filterable=True, facetable=False),  
        SearchableField(name="soluciones", type=SearchFieldDataType.String , sortable=False, filterable=True, facetable=False),  
        SearchableField(name="paginas", type=SearchFieldDataType.String , sortable=False, filterable=True, facetable=False),  
        SearchableField(name="nombre_manual", type=SearchFieldDataType.String, sortable=False, filterable=True, facetable=False),  
        SearchableField(name="referencia_url", type=SearchFieldDataType.String, sortable=False, filterable=True, facetable=False),      
        SearchableField(name="titulo", type=SearchFieldDataType.String ,sortable=True, filterable=True, facetable=False)  ,  
        SearchableField(name="subtitulo", type=SearchFieldDataType.String ,sortable=True, filterable=True, facetable=False),
        SearchableField(name="nombre_opcion", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=False),
        SearchableField(name="texto_paginas", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=False), 
        SearchableField(name="entidades", type=SearchFieldDataType.String, sortable=False, filterable=True, facetable=False), 
        SearchableField(name="preguntas_contexto", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=False), 
        SearchField(name="problemaVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
        SearchField(name="solucionesVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"), 
        SearchField(name="preguntasVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"), 
        SearchField(name="textoVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"), 
       
        
        ]
    
    # Configure the vector search configuration  
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            )
        ]
    ) 
    semantic_config = SemanticConfiguration(
    name="manual-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="paginas"),
        content_field=SemanticField(field_name="pregunta")       
        )
    )
    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index with the semantic settings
    index = SearchIndex(name=index_name, fields=fields,
                        vector_search=vector_search, semantic_search=semantic_search)
    result = index_client.create_or_update_index(index)
    print(f' {result.name} created') 
    
    
def insert_document(index_name):    
    import json    
    from azure.core.exceptions import HttpResponseError    
    import os    
   
    from azure.search.documents import SearchClient    
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]) if len(os.environ["AZURE_SEARCH_API_KEY"]) > 0 else DefaultAzureCredential()
   
    # Download the manual with embeddings  
    connection_string = os.getenv('CONNECTION_STRING')    
    file_path = "KBDEV/ManualsDocuments/ManualMobilEmbeded.json"  
    manual = g2s.download_content_as_json(connection_string, "telefonicadata", file_path)   
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]    
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]) if len(os.environ["AZURE_SEARCH_API_KEY"]) > 0 else DefaultAzureCredential()    
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)     
    for item in manual:
     item['nombre_manual'] = item.pop('nombre-manual')
     

    for item in manual:
       item['id'] = str(uuid.uuid4())
    documents = manual  
    try:    
        result = search_client.upload_documents(documents)    
        print(f"Uploaded {len(documents)} documents")    
    except HttpResponseError as e:    
        print(f"An error occurred: {e}")    
        print(f"Uploaded {len(documents)} documents")  
        
  
import os  
import uuid  
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.indexes.models import SearchIndex  
from openai import AzureOpenAI  
  
def generate_embedding(text, client, embedding_model_name="text-embedding-ada-002"):  
    """  
    Generates an embedding for the given text using Azure OpenAI Service.  
    """  
    try:  
        response = client.embeddings.create(input=text, model=embedding_model_name)  
        embedding = response.data[0].embedding  
        return embedding  
    except Exception as e:  
        print(f"Failed to generate embedding: {e}")  
        return []  
  
def insert_manual_with_embeddings(index_name):  
    """  
    Generates embeddings for specified fields in each document, then uploads the documents to Azure Cognitive Search.  
    """  
    # Azure OpenAI setup  
    from azure.core.exceptions import HttpResponseError    
    import os    
    openai_client = AzureOpenAI(  
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version="2024-02-01",  
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")  
    )  
        
     
    from azure.search.documents import SearchClient    
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]) if len(os.environ["AZURE_SEARCH_API_KEY"]) > 0 else DefaultAzureCredential()
   
    # Download the manual with embeddings  
    connection_string = os.getenv('CONNECTION_STRING')    
    file_path = "KBDEV/ManualsDocuments/ProblemasFuncionamientoPR.json"  
    manual = g2s.download_content_as_json(connection_string, "telefonicadata", file_path)   
    # Azure Cognitive Search setup  
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]  
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])  
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)  
  
    # Process documents  
    processed_documents = []  
    for doc in manual:  
        doc_id = str(uuid.uuid4())  
        problema_embedding = generate_embedding(doc["problema"], openai_client)  
        soluciones_embedding = generate_embedding(doc["soluciones"], openai_client)  
          
        processed_doc = {  
            "id": doc_id,  
            "problema": doc["problema"],  
            "tipo_problema": doc["tipo_problema"],  
            "soluciones": doc["soluciones"],  
            "paginas": doc.get("paginas", ""),  
            "nombre_manual": doc.get("nombre_manual", ""),  
            "titulo": doc.get("titulo", ""),  
            "subtitulo": doc.get("subtitulo", ""),  
            "nombre_opcion": doc.get("nombre_opcion", ""),  
            "texto_paginas": doc.get("texto_paginas", ""),  
            "problemaVector": problema_embedding,  
            "solucionesVector": soluciones_embedding  
        }  
          
        processed_documents.append(processed_doc)  
      
    # Upload documents  
    try:  
        result = search_client.upload_documents(processed_documents)  
        print(f"Uploaded {len(processed_documents)} documents successfully.")  
    except Exception as e:  
        print(f"Failed to upload documents: {e}")  
  
def insert_manual_roaming_with_embeddings(index_name):  
    """  
    Generates embeddings for specified fields in each document, then uploads the documents to Azure Cognitive Search.  
    """  
    # Azure OpenAI setup  
    from azure.core.exceptions import HttpResponseError    
    import os    
    openai_client = AzureOpenAI(  
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version="2024-02-01",  
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")  
    )  
        
     
    from azure.search.documents import SearchClient    
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]) if len(os.environ["AZURE_SEARCH_API_KEY"]) > 0 else DefaultAzureCredential()
   
    # Download the manual with embeddings  
    connection_string = os.getenv('CONNECTION_STRING')    
    file_path = "KBDEV/ManualsDocuments/RoamingPage60PR.json"  
    manual = g2s.download_content_as_json(connection_string, "telefonicadata", file_path)   
    manual_json_string = json.dumps(manual)
    # Azure Cognitive Search setup  
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]  
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])  
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)  
  
    # Process documents  
    chunk_id = 0
    processed_documents = []    
    for doc_list in manual:  
        for doc in doc_list:  
            try:  
                doc_id = str(uuid.uuid4())  
                problema = doc["problema"]  
                
                problema_embedding = generate_embedding(doc["problema"], openai_client)  
                soluciones_embedding = generate_embedding(doc["soluciones"], openai_client)  
                text_embedding = generate_embedding(doc["page_text"], openai_client)  
                soluciones_found = doc["soluciones"]
                # Iterate over PreguntasContexto list  
                # Concatenate all questions into a single string  
                Preguntas = ' '.join([json.dumps(pregunta, ensure_ascii=False) for pregunta in doc["PreguntasContexto"]])  
              
                preguntas_embedding = generate_embedding(Preguntas, openai_client)  
                chunk_id += 1
    
                # Convert entidades dictionary into a string  
                Entidades = ' '.join([json.dumps(pregunta, ensure_ascii=False) for pregunta in doc["entidades"]])  
                processed_doc = {  
                        "id": doc_id,  
                        "problema": doc["problema"],  
                        "tipo_problema": doc["tipo_problema"],  
                     ##    "soluciones": doc["soluciones"],  
                         "paginas": doc.get("paginas", ""),  
                        "nombre_manual": doc.get("nombre_manual", ""),  
                       "titulo": doc.get("titulo", ""),  
                        "subtitulo": doc.get("subtitulo", ""),  
                       "nombre_opcion": doc.get("nombre_opcion", ""),  
                         "texto_paginas": doc.get("page_text", ""),  
                        "problemaVector": problema_embedding,  
                        "referencia_url": doc.get("referencia_url", ""),  
                       "solucionesVector": soluciones_embedding ,
                       "preguntasVector": preguntas_embedding,
                        "preguntas_contexto": Preguntas,
                       "textoVector": text_embedding,
                         "entidades": Entidades, 
                       ##  "chunk_id": str(chunk_id)
                    }  
                    
                processed_documents.append(processed_doc)  
    
            except KeyError as e:  
                     print(f"Key {str(e)} not found in dictionary: {doc}")  
                          
            
      
    # Upload documents  
    try:  
        result = search_client.upload_documents(processed_documents)  
        print(f"Uploaded {len(processed_documents)} documents successfully.")  
    except Exception as e:  
        print(f"Failed to upload documents: {e}")  


def insert_manual_roaming_chunking_with_embeddings(index_name):  
    """  
    Generates embeddings for specified fields in each document, then uploads the documents to Azure Cognitive Search.  
    """  
    # Azure OpenAI setup  
    from azure.core.exceptions import HttpResponseError    
    import os    
    openai_client = AzureOpenAI(  
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version="2024-02-01",  
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")  
    )  
        
     
    from azure.search.documents import SearchClient    
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]) if len(os.environ["AZURE_SEARCH_API_KEY"]) > 0 else DefaultAzureCredential()
   
    # Download the manual with embeddings  
    connection_string = os.getenv('CONNECTION_STRING')    
    file_path = "KBDEV/ManualsDocuments/RoamingPage110PR.json"  
    manual = g2s.download_content_as_json(connection_string, "telefonicadata", file_path)   
    manual_json_string = json.dumps(manual)
    # Azure Cognitive Search setup  
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]  
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])  
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)  
  
    # Process documents  
    chunk_id = 0
    processed_documents = []    
    for doc_list in manual:  
        for doc in doc_list:  
            try:  
                doc_id = str(uuid.uuid4())  
                problema = doc["problema"]  
                chunks = text_splitter.split_text(doc["page_text"])
                
                print(f"Number of chunks: {len(chunks)}")
                for chunk in chunks: 
                    
                    text_embedding = generate_embedding(chunk, openai_client)  
                    soluciones_found = doc["soluciones"] 
                    Preguntas = ' '.join([json.dumps(pregunta, ensure_ascii=False) for pregunta in doc["PreguntasContexto"]])   
                    preguntas_embedding = generate_embedding(Preguntas, openai_client)  
                    chunk_id += 1 
                    Entidades = ' '.join([json.dumps(pregunta, ensure_ascii=False) for pregunta in doc["entidades"]])  
                    processed_doc = {  
                            "id": doc_id,  
                            "problema": doc["problema"],  
                            "tipo_problema": doc["tipo_problema"],  
                        ##    "soluciones": doc["soluciones"],  
                            "paginas": doc.get("paginas", ""),  
                            "nombre_manual": doc.get("nombre_manual", ""),  
                            "titulo": doc.get("titulo", ""),  
                            "subtitulo": doc.get("subtitulo", ""),  
                            "nombre_opcion": doc.get("nombre_opcion", ""),  
                            "texto_paginas": doc.get("page_text", ""),   
                            "referencia_url": doc.get("referencia_url", ""),   
                            "preguntasVector": preguntas_embedding,
                            "preguntas_contexto": Preguntas,
                            "textoVector": text_embedding,
                            "entidades": Entidades, 
                            "chunk_id": str(chunk_id)
                        }  
                    
                    processed_documents.append(processed_doc)  
    
            except KeyError as e:  
                     print(f"Key {str(e)} not found in dictionary: {doc}")   
    # Upload documents  
    try:  
        result = search_client.upload_documents(processed_documents)  
        print(f"Uploaded {len(processed_documents)} documents successfully.")  
    except Exception as e:  
        print(f"Failed to upload documents: {e}")  
  


def VectorQASearch(index_name, question):    
    from azure.search.documents.models import VectorizedQuery  
   
    
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]) if len(os.environ["AZURE_SEARCH_API_KEY"]) > 0 else DefaultAzureCredential()
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]   
    query = question
    from openai import AzureOpenAI
    client = AzureOpenAI(
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version = "2024-02-01",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    embedding_model_name = "text-embedding-ada-002"
    embedding = client.embeddings.create(input=query, model=embedding_model_name).data[0].embedding
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields="preguntaVector")
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    results = search_client.search(  
        search_text=None,  
        vector_queries= [vector_query],
        select=["pregunta", "respuesta", "pagina"],
    )  
           
    results_list = [{'pagina': result['pagina'], 'respuesta': result['respuesta'], 'score': result['@search.score']} for result in results]
    return results_list

def VectorManualSolutionsSearch(index_name, question, manualName):    
    from azure.search.documents.models import VectorizedQuery   
    from openai import AzureOpenAI
    from azure.core.exceptions import AzureError

    try:
        credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]) if len(os.environ["AZURE_SEARCH_API_KEY"]) > 0 else DefaultAzureCredential()
        endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]   
        query = question
        client = AzureOpenAI(
            api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version = "2024-02-01",
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        embedding_model_name = "text-embedding-ada-002"
        embedding = client.embeddings.create(input=query, model=embedding_model_name).data[0].embedding
        vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=2, fields="preguntasVector")
        vector_query_preguntas = VectorizedQuery(vector=embedding, k_nearest_neighbors=2, fields="preguntasVector")
        vector_query_texto = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields="textoVector")
        search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
       
         
        filter_expression = f"nombre_manual eq '{manualName}'" 


        results = search_client.search(  
            search_text=None,   
            vector_queries= [ vector_query_preguntas, vector_query_texto ],
            select=[ "soluciones", "texto_paginas", "paginas", "preguntas_contexto", "titulo", "subtitulo"],
            filter=filter_expression,
        )  
               
        results_list = [{'preguntas': result['preguntas_contexto'], 'titulo': result['titulo'],
                         'subtitulo': result['subtitulo'], 'paginas': result['paginas'],
                         'soluciones': result['texto_paginas'],
                         'score': result['@search.score']} for result in results]
        return results_list

    except AzureError as e:
        print(f"An Azure error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")