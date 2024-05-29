import asyncio
from queue import Full
from jinja2 import Undefined
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, AzureChatCompletion 
from dotenv import load_dotenv 
from azure.core.credentials import AzureKeyCredential 
import os
from openai import AzureOpenAI 
import Tools as tools 
from services import Service
import searchaiservice as search
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import (
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.prompt_template.input_variable import InputVariable
from semantic_kernel.prompt_template import PromptTemplateConfig
load_dotenv(override=True) # take environment variables from .env.
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
# The following variables from your .env file are used in this notebook
endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
credential = AzureKeyCredential(os.environ["AZURE_SEARCH_ADMIN_KEY"])  
index_name = os.environ["AZURE_SEARCH_INDEX"]
azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
azure_openai_key = os.environ["AZURE_OPENAI_KEY"] if len(os.environ["AZURE_OPENAI_KEY"]) > 0 else None
azure_openai_embedding_deployment = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
embedding_model_name = os.environ["AZURE_OPENAI_EMBEDDING_MODEL_NAME"]
azure_openai_api_version = os.environ["AZURE_OPENAI_API_VERSION"]
azure_end_point = os.environ["AZURE_OPENAI_ENDPOINT"]
deployment = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
api_key = os.environ["AZURE_OPENAI_API_KEY"]
from semantic_kernel.prompt_template import PromptTemplateConfig
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json
movilData = {  
    "Plan": "Test Plan",  
    "Capacidad GB": 100,  
    "Capacidad Voz": 500,  
    "Capacidad SMS": 1000,  
    "Roaming Dias": 10,  
    "Tipo Cliente": "Prepago",  
    "Tipo Plan": "Anual",  
    "Saldo GB": 00,  
    "Saldo voz": 250,  
    "Saldo Roaming Dias": 5,  
    "Saldo Roaming Argentina-Brasil": 3,  
    "Saldo $ (aplica solo para prepago)": 100,  
    "Deudas Total": 0,  
    "Deuda Vencida": 0,  
    "Cuotas de Equipo": 10,  
    "Suspendido": False,  
    "Equipo": "Phone Model",  
    "Reinicio del plan": "2023-01-01",  
    "Datos RED (NAM)": "Test Data",  
    "DATOS BSS": "Test Data",  
    "Roaming RED": "Test Data",  
    "Roaming BSS": "Test Data",  
    "SMS RED": "Test Data",  
    "SMS BSS": "Test Data",  
    "Voz RED": "Test Data",  
    "VOZ BSS": "Test Data",  
    "Suspension RED (CUSTOM 14)": "Test Data",  
    "VOLTE RED": "Test Data",  
    "VO WIFI": "Test Data",  
    "MAX Velocidad Navegacion (Estrangulacion)": 100,  
    "Registrado en la red?": True,  
    "Operador Conectado?": True,  
    "Ultima conexion": "2022-01-01",  
    "llamadas LDI": 10  
}  

manualNames = {"Roaming": "Manual de procedimientos de Telefonica Chile", 
               "Cobertura": "Manual de procedimientos de Telefonica Chile",}
 

businessLogic = """
   JSON para toma de decisiones
   
```{  
  "ProblemaCliente": "No Navega",  
  "Saldo GB": 10,  
  "DeudaVencida": 0,  
  "Suspendido:: "No",
  "Registrado en la red?": "NO",
  "Condiciones": {  
    "CondicionSaldo": "Saldo GB == 0",  
    "CondicionDeuda": "DeudaVencida > 100"  
  },  
  "LogicaNegocio": {  
    "Reglas": [  
      {  En caso de que el cliente este en Saldo GB 0 , o Deuda Vencida > 100, o Suspendido == Si o Registrado en la red? == NO
         Explicarle al ejecutivo por que no puede navegar y explicarle en detalle la situacion
         En caso que todo esta bien, usar el contexto del manual para explicarle como resolver el problema. Esto el ejecutivo tiene 
         que reportarlo al cliente. Se breve y conciso.
      },  
    ]  
  }  
}  

```  
Please replace "xxx" with the actual amount you want to inform the customer about. Note that this JSON just represents your logic and isn't actual code that can be executed.
"""

async def analyze_document_problems(document,  nombreDocumento, pagina):
    kernel = sk.Kernel()  
   
    service_id = "default" 
    
    kernel.add_service(
        AzureChatCompletion(service_id=service_id, deployment_name=deployment,  api_version="2024-05-01-preview",
                            endpoint=azure_end_point, api_key=api_key)
    )
    req_settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
    req_settings.max_tokens = 15000
    req_settings.temperature = 0.0
    req_settings.top_p = 0.8
    
    
     
    prompt = """  
    
        system: 
            # Eres un experto de Telefonica Chile.
            # Contexto: Estas trabajando en el centro de llamadas de Telefonica Chile y recibes una llamada de un cliente que tiene problemas con su telefono movil.
            # Tu tarea es leer este manual de procedimientos y crear por cada seccion area una lista de problemas que se pueden resolver con este documento.
            # Instrucciones paso a paso:
                1) Navegar sobre el documento encontrando Titulos, subtitulos y acciones a tomar dependiendo de la situacion presentada.
                2) Por cada titulo y subtitulo, encuentra el problema y las opciones de resolucion dependiendo de la situacion.
                7) Extrae todas las entidades en cada problema que encuentres por ejemplo :
                    cobertura: "Mexico, Chile, Argentina", Nombre Cliente: "Juan Perez", ciudades Cobertura: "Santiago, Buenos Aires" etc.
                3) Usa la logica de un arbol de decisiones para crear las opciones de resolucion.
                4) Es muy importante que analices cada pagina del documento. Aqui esta todo el texto: procesa cada pagina y extrae los problemas hasta la pagina 10.
                5) Describe en detalle la solucion para cada caso.
                
                6) La estructura del documento es 
                     Titulo
                     Subtitulo Opcion1
                        Opciones
                         pasos para resolver
                     Subtitulo Opcion2
                        Opciones
                            pasos para resolver
                    Da tu reporte por cada Titulo.Subtitulo_Opcion-Opciones
                       PASOS
                7) Crea una lista de lo mas que puedas preguntas y respuestas que puedan apoyar al ejecutivo a resolver el problems
                   todo basado en la informacion del texto. Por ejemplo:
                   Que covertura tiene: Mexico, Chile, Argentina etc.
               
                     
           En cada linea puede haber informacion que te indique un problema a resolver , opciones y pasos para resolverlo. 
           Este es el documento donde cada pagina termina en Pagina | 1, Pagina | 2, etc.
            ###START###
              {{$texto}}
            ###END###
           
            Describe el tipo de problema de esta lista
            {{$tipos_problema}}
            ## Importante
            Asegurate de incluir todas las entidades encontradas toda la lista por ejemplo:
            Todos los Paises como :Cobertura continua Brasil Bulgaria Canadá China Colombia Costa Rica Croacia Dinamarca Ecuador"
            esto es muy importante ya que lo usamos para notificar al cliente. Incluye todo el detalle posible en tu respuesta.
            
            Respuesta: siempre en JSON no comentarios solo el JSON  
            Este arreglo tendra problemas detectados en  el documento guiate por los titulos y subtitulos. Ponlos todos todos todos.
                [  
                       {    
                            'problema': 'xxxxxxxxxxxxx',    
                            'tipo_problema': 'xxxxxxxxxxxxx',    
                            'soluciones': 'xxxxxxxxxxxxx',  
                            'paginas': '1,2,3',    
                            'referencia_url': 'yyyyyyyyyyyyy',    
                            'nombre_manual': 'yyyyyyyyyyyyy',    
                            'titulo': 'Navegacion Internet Movil',    
                            'subtitulo': 'Cliente con informacion flash',  
                            'nombre_opcion': 'xxxxx',  
                            'entidades': {  
                                'cobertura': 'Mexico, Chile, Argentina',   
                                'Nombre Cliente': 'Juan Perez',   
                                'ciudades Cobertura': 'Santiago, Buenos Aires' 
                                'aplicaciones': 'Facebook, WhatsApp, Instagram'
                                'equipos': 'Samsung Galaxy S20, iPhone 12, etc'
                                'nombres': 'Juan Perez, Maria Perez, etc'
                                'numeros': '1234567890, 0987654321, etc'
                                'Paices': 'Mexico, Chile, Argentina, etc' IMPORTANTE! Menciona todos los paices en el documento
                                 
                            }
                            PreguntasContexto:
                            [
                              {
                                  "pregunta1": "yyyyyyyyyyyyy",  
                                  "respuesta1": "yyyyyyyyyyyyy",
                              },
                              {
                                  "pregunta2": "yyyyyyyyyyyyy",  
                                  "respuesta2": "yyyyyyyyyyyyy",
                              },
                            ],
                           
                    }   

        ]  

 
    
    """
    
    prompt_template_config = PromptTemplateConfig(
    template=prompt,
    name="extract",
    template_format="semantic-kernel",
    execution_settings=req_settings,
)
    with open('classifications.txt', 'r') as f:
        content = f.read()
    function = kernel.add_function(
            function_name="extract_problems",
            plugin_name="extract_plugin",
            prompt_template_config=prompt_template_config,
        )
 
   
    try:
        result = await kernel.invoke(function, texto=document, tipos_problema=content)
        responseSTR = str(result)

        # Convert result from a string to a list of dictionaries
        result = json.loads(responseSTR)

        # Add the new property to each dictionary
        for record in result:
            record['page_text'] = document
            record['id']= nombreDocumento + "_" + str(pagina)

        # Convert result back to a string
        response = json.dumps(result, ensure_ascii=False)
    except Exception as e:
        response = f"An error occurred: {str(e)}"

    return response
    

# This asynchronous function analyzes a document for QA using the OpenAI GPT-4 model. 
# It sets up a kernel with the AzureChatCompletion service, configures the request settings, and defines a prompt for 
# the model to generate questions and answers based on the document content.
async def analyze_document_QA(document, totaltokens):
    kernel = sk.Kernel()  
    service_id="chat-gpt"
    deployment, api_key, endpoint= azure_openai_settings_from_dot_env()
    
    service_id = "default"
    
    service_id="chat-gpt"
    
    
    kernel.add_service(
        AzureChatCompletion(service_id=service_id, deployment_name=deployment, endpoint=endpoint, api_key=api_key),
    )
    
    req_settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
    req_settings.max_tokens = 20000
    req_settings.temperature = 0.1
    req_settings.top_p = 0.8
    
    prompt = """  
    
        system: 
            # Eres un experto de Telefonica Chile y comoces los problems que tienen los clientes con sus mobiles muy bien. 
            # Tu tarea leer este manual de procedimientos y crear por cada seccion area una lista 
             de preguntas y respuestas. Trata de lograr 100 preguntas y respuestas.
            ##Tus objetivos: 
                    1) Identifica todas las preguntas posibles que se pueden contestar con este document.
                    2) Detalla tu respuesta lo mas posible para que el cliente de Telefonica Chile pueda entenderla
                    3) Tu meta es lograr llegar a 100 preguntas y respuestas o muchas mas que se pueden resolver para el cliente de Telefonica Chile con la informacion
                    de este documento
                    ## Importante trata lo mas que puedas!
                    4) Desarrolla por lo menos 100 preguntas y respuestas. Lee todo el manual y trata de hacer preguntas y respuestas en detalle 
                    5) Estas preguntas tambien pueden ser problemas que el cliente de Telefonica Chile puede tener
                       y que se resuelven con este manual. Asi que orienta la pregunta como posible problema tambien.
                    6) No olvides de extraer entidades como nombres de personas, numeros, nombres de equipos, etc contenidos en el texto
                    de tu respuesta
                    7) Detecta que problema esta respuesta puede resolver del cliente en Telefonica Chile? Navegar, llamadas, cobertura, etc
                
             
            ## Instrucciones del proceso;
                ## 1) Lee el texto que esta conformado por pararrafos en lineas de por una o mas paginas
                ## 2) El docuemto contine titulos, y subtitilos. Responde basados en eso titulos:
                    Ejemplo: Navageacion Internet Movil es un titulo usalo como contexto al crear tus preguntas y respuestas
                    Ejemplo2: Clinte con informaicon flash : Es un subtitulo usalo como contexto al crear tus preguntas y respuestas
                    Ejemplo3 Atencion 1era Linea: etc.
                
            Este es el contenido de las paginas del manual "Procedimientos/ Reclamos / Problemas de Funcionamiento"
            ###START###
            {{$texto}}
            ###END###
            
            Respuesta: siempre en JSON no ocmentarios solo el JSON termina todas las paginas en JSON
            [  
                
                {  
                    "pregunta": "yyyyyyyyyyyyy",  
                     "respuesta": "yyyyyyyyyyyyy",
                     "pagina: "yyyyyyyyyyyyy"
                     "nombre-manual": "yyyyyyyyyyyyy"
                     "titulo": "Navegacion Internet Movil"
                     "subtitulo": "Cliente con informacion flash"
                     "problemas-resolver": "" "Detecta el problema basado en la pregunta y la respuesta" Usa tu conocimiento de Telefonica Chile
                      para detectar el problema que se resuelve con esta pregunta y respuesta
                      
                }  
]  

 
    
    """
    
    prompt_template_config = PromptTemplateConfig(
    template=prompt,
    name="extract",
    template_format="semantic-kernel",
    execution_settings=req_settings,
        )
    with open('classifications.txt', 'r') as f:
        content = f.read()
    function = kernel.add_function(
            function_name="extract_problems",
            plugin_name="extract_plugin",
            prompt_template_config=prompt_template_config,
        ) 
    
    result = await kernel.invoke(function, texto=document, tipos_problema=content)
    response = str(result)
    return  response;  

async def TestOpenAI():
    from semantic_kernel import Kernel
   
    service_id = None
    kernel = Kernel()
        
    service_id = "default"
    kernel.add_service(
            AzureChatCompletion(service_id=service_id, deployment_name="gpt4turbo",  
                                endpoint="https://workshopopenaisw.openai.azure.com/", api_key="d8dac145316a42319fbbb1f053161a83")
        )
    plugins_directory = "prompts" 
    funFunctions = kernel.add_plugin(parent_directory="Prompts", plugin_name="Plugins") 
    callFunction = funFunctions["ClassifyProblem"] 
    from semantic_kernel.functions import KernelArguments  
    joke = await kernel.invoke(callFunction)
    print(joke)
    
    
async def classify_problem(problem_solution_pairs: list):
    
    problem_solution_pairs_json = json.dumps(problem_solution_pairs)
    totalTokens = tools.num_tokens_from_string(problem_solution_pairs_json, "cl100k_base")
    categorias = ""
    with open('categories.txt', 'r') as f:
        categorias = f.read()
    kernel = sk.Kernel()  
    service_id="chat-gpt"
    deployment, api_key, endpoint= azure_openai_settings_from_dot_env()
    
    service_id = "default"
    
    service_id="chat-gpt"
    
    
    kernel.add_service(
        AzureChatCompletion(service_id=service_id, deployment_name=deployment, endpoint=endpoint, api_key=api_key),
    )
    
    req_settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
    req_settings.max_tokens = 21000
    req_settings.temperature = 0.0
    req_settings.top_p = 0.0
    
    prompt = """  
    
        system: 
            # Eres un experto de Movistar Chile  y tienes una idea clara de  los problems que tienen los clientes con sus moviles muy bien. 
            # Instrucciones:
            # 1) Tu tarea leer la lista  numerados con numeros aleatorios  problemas y soluciones y clasificarlos en una de las categorias ademas de lo 
              que se te indica abajo.
              Asegurate de ver todos los problemas y procesarlos uno por uno. Muy IMPORTANTE!
            # 2) Del problema extrae entidades tales como nombres de personas, tipo servicio (roaming), tipo de equipo (iphone),
                # nombre equipo (Samsung Galaxy S20), direccion casa 
            # 4) Clasifica el problema en una de las categorias que se encuentran en el archivo de categorias, si identificas mas de una categoria 
                escoge todas las que aplican (cat1, cat2, cat3). Asegurate de escoger la categoria correcta y usar ese nombre.
              4b) Clasifica tambien el problema como tecnico o comercial
            # 5) Finalmente ve el problema y basado en tu conocimiento de Telefonica Chile y en la solucion redacta una solucion
                que se ajuste al problema y que sea facilmente entendida for el ejecutivo del cento de llamadas.
               6) Explicar por que se escogio esa categoria
               7) Es IMPORTANTE que se escoja la categoria correcta para el problema. No inventes ni asumas escoje las mejor(es) opciones.
                  esto es muy importante para poder detectar problemas en el futuro
                8)No olvides en extraer entidades como CTOs, numeros, nombres de personas, etc
                9) Asegurate de contestar todas las preguntas y analizar las respuestas
                10)Nota: Si el problema o la solucion incluye prueba de la CTO 16 (U otro caso), asegurate 
                   de clasificarlo como "Linea Telefonica fija" y "ProblemaTecnico".
                 
                    
             ###START###
                    {{$categorias}}
             ###END###
             
            ## Esta es la lista de problemas y soluciones. Ejecuta una a la vez generando el reporte para cada uno 
              con el json que se indica abajo . 
              ###START###
            {{$listaproblemas}}
              ###END###
            # 
            ## IMPORTANTE!   No quiero explicaciones del proceso solo reporta en JSON todos los problemas 
            Crea un JSON puro sin /n
            IMPORTANTE: Asegurate de leer los 5 registros que te doy en la lista de problemas.
            Respuesta: siempre en JSON no comentarios  solo el JSON procesa todos los registros
            [  {  
                        "problema#: "1", IMPORTANTE PONER EL NUMERO DE PROBLEMA
                        "clasificacion": "ProblemaTecnico" O "ProblemaComercial"
                        "problema": "El cliente no expuso una problemática en la conversación.",  
                        "problema-entidades": "NombreCliente: XXXX, "NumeroTelefono" "XXX", "tipoTelefono": "Samsung", etc ,
                        "problema-tecnico": "El cliente no puede hacer llamadas internacionales", 
                        "category": "Roaming", 
                        "manual-recomendado": "Manual de roaming", 
                        "solucion-mejorada": "El ejecutivo ayudó al cliente a verificar la información de su cuenta y a certificar la CTO número 9. Además, se le proporcionó información adicional sobre cómo mantener su cuenta segura y actualizada." 
                          
                 }  
                ]  

    
    """
    prompt_template_config = PromptTemplateConfig(
    template=prompt,
    name="extract",
    template_format="semantic-kernel",
    execution_settings=req_settings,
        )
    
    function = kernel.add_function(
            function_name="extract_problems",
            plugin_name="extract_plugin",
            prompt_template_config=prompt_template_config,
        )

 
    
    result = await kernel.invoke(function, categorias=categorias, listaproblemas=problem_solution_pairs_json)
    response = str(result).replace('\n', '')
    return  response;   
    
    
async def SetSolution(problem_solution_pairs: list, ManualAcademia: str):
    
    problem_solution_pairs_json = json.dumps(problem_solution_pairs)
    totalTokens = tools.num_tokens_from_string(problem_solution_pairs_json, "cl100k_base")
    content = ""
    
    kernel = sk.Kernel()  
    service_id="chat-gpt"
    deployment, api_key, endpoint= azure_openai_api_version()
    
    service_id = "default"
    
    service_id="chat-gpt"
    
    
    kernel.add_service(
        AzureChatCompletion(service_id=service_id, deployment_name=deployment, endpoint=endpoint, api_key=api_key),
    )
    
    req_settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
    req_settings.max_tokens = 20000
    req_settings.temperature = 0.1
    req_settings.top_p = 0.8
    
    prompt = """  
    
        system: 
            # Eres un experto de Telefonica Chile y comoces los problems que tienen los clientes con sus mobiles muy bien. 
            # Tu tarea leer la lista  problemas y soluciones y encontrar una posible solucion en el manaul academico
              de Telefonica Chile que contiene preguntas y respuestas para los ejecutivos de call center. Estas se usan para 
              ayudar a los ejecutivos a resolver problemas de los clientes.
            # cada elemento de la lista tiene el problema  vas a darme una solucion nueva
              con informacion extraida del manual academico o datos del web site de telefonica chile que tiene preguntas y soluciones o descripcion de problemas y soluciones
              No inventes nada solo describe la solucion si  existe para el problema que se te da. Podras encontrar el problema en la lista de problemas.  
              
            # Si no encuentras una solucion solo di 'No hay solucion en el manual' 
            
            ###START###
            {{$listaproblemas}}
            ###END### 
            
            Este el el manual que te va a ayudar a encontrar la solucion. Importante!
            ###START###
            {{$ManualAcademia}}
            ###END###
            
            Respuesta: siempre en JSON no ocmentarios solo el JSON procesa todos los registors
            [  {  
                        "problema#: "1",
                        "problema": "El cliente no expuso una problemática en la conversación.",   
                        "solution_academico": "El ejecutivo ayudó al cliente a verificar la información de su cuenta y a certificar la CTO número 9. Además, se le proporcionó información adicional sobre cómo mantener su cuenta segura y actualizada.",  
                        "solution_steps": {  
                            "step1": "Identificar la falta de un problema específico en la conversación.",  
                            "step2": "Ayudar al cliente a verificar la información de su cuenta.",  
                            "step3": "Certificar la CTO número 9.",  
                            "step4": "Proporcionar información adicional sobre la seguridad y actualización de la cuenta.",  
                            "step5": "Finalizar la conversación asegurándose de que el cliente está satisfecho con la información proporcionada."  
                        }  
                 }  
                ]  

    
    """
    
    prompt_template_config = PromptTemplateConfig(
    template=prompt,
    name="extract",
    template_format="semantic-kernel",
    execution_settings=req_settings,
        )
    
    function = kernel.add_function(
            function_name="extract_problems",
            plugin_name="extract_plugin",
            prompt_template_config=prompt_template_config,
        )

 
    
    result = await kernel.invoke(function, ManualAcademia=ManualAcademia, listaproblemas=problem_solution_pairs_json)
    response = str(result)
    return  response;  


async def classify_question(problem : str):
    content = ""
    with open('classifications.txt', 'r') as f:
        content = f.read()
    kernel = sk.Kernel()  
    service_id="chat-gpt" 

    deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
    service_id = "default"
    kernel.add_service(
        AzureChatCompletion(service_id=service_id, deployment_name=deployment, endpoint=endpoint, api_key=api_key),
    )
    
    plugins_directory = "prompts" 
    funFunctions = kernel.import_plugin_from_prompt_directory(plugins_directory, "plugins") 
    callFunction = funFunctions["ClassifyProblem"] 
    result = await kernel.invoke(callFunction, sk.KernelArguments(problema=problem, tipos_problema=content)) 
    response = str(result)
    return  response;  


async def recomienda_solucion(problema, casos):
    kernel = sk.Kernel()  
    service_id="chat-gpt"
    

    deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
    service_id = "default"
    kernel.add_service(
        AzureChatCompletion(service_id=service_id, deployment_name=deployment, endpoint=endpoint, api_key=api_key),
    )
    
    plugins_directory = "prompts"

    funFunctions = kernel.import_plugin_from_prompt_directory(plugins_directory, "plugins")
    

    callFunction = funFunctions["Recomiendasoluciones"] 
    result = await kernel.invoke(callFunction, sk.KernelArguments(input=problema, casos=casos)) 
    return  result;  

async def create_Embedding(Text):
    # Create an instance of the AzureOpenAI class
     
    client = AzureOpenAI(
            api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version = "2024-02-01",
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            )
    response = client.embeddings.create(input = [Text], model='text-embedding-ada-002').data[0].embedding
    return response

async def telefonica_ai_agent(query: str):
    import os, dotenv
    import openai
    searchresults =search.VectorManualSolutionsSearch("manual_roaming_solutions_chunking_index",query)
    max_response_tokens = 20000
    overall_max_tokens = 30000
    prompt_max_tokens = overall_max_tokens - max_response_tokens
    contexto = json.dumps(searchresults)
  
    
    prompt = f"""  
        ##Systema: Eres un experto de Telefonica Chile y conoces los problems que tienen los clientes con sus mobiles muy bien.
        ##Rol: Contestar las preguntas o problemas que tengan los clientes nasados en la informacion y reglas de negocio que te dare.
        ##Instrucciones:
          1) Problema: El cliente no puede navegar en internet o hacer llamadas
          2) Importante: El mensaje es para el ejecutivo del centro de llamadas de Telefonica Chile no para el cliente. Dirijete al ejecttivo.
          3) Reporta todo el detalle posible en tu respuesta. Usa el contexto del manual para explicarle como resolver el problema.
     
                  
           ### Contexto:  {contexto} ###END###
        
        
            
                     
        """
    
    prompt = prompt.encode('latin1').decode('unicode_escape')
    system_message = f"{prompt.strip()}"
    user_message =  query
    
    messages=[
    {"role": "system", "content": system_message},
    {"role": "user", "name":"chileejecutivo", "content": user_message} 
    ]
    token_count = num_tokens_from_messages(messages)  
    deployment_name= os.environ['AZURE_OPENAI_DEPLOYMENT_NAME']
    # remove first message while over the token limit
    while token_count > prompt_max_tokens:
        messages.pop(0)
    token_count = num_tokens_from_messages(messages)
    response = send_message(messages, deployment_name, max_response_tokens)
    messages.append({"role": "assistant", "content": response})
    responseMessage = {"role": "assistant", "content": response}
    messages.append(responseMessage)

    return responseMessage

import tiktoken
def num_tokens_from_contents_chat(contents, model="gpt-3.5-turbo-0301"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for content in contents:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += len(encoding.encode(content))
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens

def num_tokens_from_string(content, model="gpt-3.5-turbo-0301"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
    num_tokens += len(encoding.encode(content))
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens

def send_message(messages, model_name, max_response_tokens=500):
    import os, dotenv
    import openai
    
    azure_openai_api_version = os.environ["AZURE_OPENAI_API_VERSION"]
    azure_end_point = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
 
        
    client = openai.AzureOpenAI(
        azure_endpoint = azure_end_point, 
         
        api_key=api_key,  
        api_version="2024-05-01-preview"
    )
    response = client.chat.completions.create(
        model="gpt4turbo",
        
        messages=messages,
        temperature=0.5,
        max_tokens=max_response_tokens,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content

# Defining a function to print out the conversation in a readable format
def print_conversation(messages):
    for message in messages:
        print(f"[{message['role'].upper()}]")
        print(message['content'])
        print()
        
#################  

    
kernel = sk.Kernel()  
service_id = "aoai_chat_completion"
    
kernel.add_service(
        AzureChatCompletion(service_id=service_id, deployment_name=deployment,  api_version="2024-05-01-preview",
                            endpoint=azure_end_point, api_key=api_key)
    )


execution_settings = OpenAIChatPromptExecutionSettings(
    service_id=service_id,
    ai_model_id="gpt4turbo",
    max_tokens=15000,
    temperature=0.7,
) 
chat_history = ChatHistory()
chat_history.add_system_message("Eres un experto en Telefonica Chile y conoces los problemas que tienen los clientes con sus móviles muy bien.")
 
    # Process the user message and get an answer
usuario_ultimaPregunta = [] 

### Semantic Kernel
### This function is used to process the user input and generate a response using the Semantic Kernel
### It uses the OpenAI GPT-4 model to generate the response based on the user input and the context of the conversation
### The response is generated by the Semantic Kernel using the Azure Chat Completion service
### The response is then returned to the user
### The function also updates the chat history with the user input and the generated response
### The function also updates the global variable `usuario_ultimaPregunta` with the user input
###     


async def semantic_agent(input_text: str): 
    global usuario_ultimaPregunta 
    import os, dotenv
    import openai
     
    
    usuario_ultimaPregunta_str = ' '.join(usuario_ultimaPregunta)
    intent = await get_intent(input_text, usuario_ultimaPregunta_str)
        
    tipo = intent["tipo"]
    tipo_problema_pregunta = intent["tipo_problema_pregunta"]
    pregunta_mejorada = intent["pregunta_mejorada"]
    categoria = intent["categoria"]
    if(tipo_problema_pregunta == "ProblemaTecnico"):
            categoria = categoria.strip()
            default_value = "Manual de procedimientos de Telefonica Chile"  # replace with your actual default value
            manualName = manualNames.get(categoria, default_value)
        
            searchresults =search.VectorManualSolutionsSearch("manual_roaming_solutions_chunking_index", pregunta_mejorada, manualName)
            max_response_tokens = 20000
            overall_max_tokens = 30000
            prompt_max_tokens = overall_max_tokens - max_response_tokens
            contexto = json.dumps(searchresults)
            prompt = """  
                ##Systema: Eres un experto de Telefonica Chile y conoces los problems que tienen los clientes con sus mobiles muy bien.
                ##Rol: Contestar las preguntas o problemas que tengan los clientes nasados en la informacion y reglas de negocio que te dare.
                ##Instrucciones:
                1) Situaico: El ejecutivo esta hablando con el clinete y tiene una pregunta o un problema
                2) Importante: El mensaje es para el ejecutivo del centro de llamadas de Telefonica Chile no para el cliente. Dirijete al ejecttivo.
                3) Reporta todo el detalle posible en tu respuesta. Usa el contexto del manual para explicarle como resolver el problema.
                4) Idenitfica el intento si es una pregunta o un problema. Responde de acuerdo a la situacion (pregunta o problema).
                5) Trata de usar logica para intuir y deducir. Por ejemplo si te preguntan que Paises en Latin America no tienen cobertura
                    usa la lista para deducir cuales not tienne cobertura usando to informacion de la region.
                6) IMPORTANTE!! Cuando se trata de coberturas se conciso dale al ejecutivo toda la informaicon que encuentres no lo mandes
                    otra vez a leer el manual. Dale respuestas acertivas y listas para el cliente 
                    busca cuidadosamente en la list ahi esta la respuesta de regiones, paises, ciudades, etc.
                7) Esta es la historia de la conversation donde encontraras las ultimas preguntas, el contexto y tu respuesta. 
                
                    usalo en forma inteligente para que la conversacion tenga continuidad
                    ### Start
                    {{$history}}
                    ### END
                6) Al principio di algo como: Entiendo que la pregunta cel cliente es sobre... o El problema del cliente es...
                    o entiendo que el cliente tiene un problema con...  Nuevo contesto para contestar la pregunta     {{$input_text}}
                        
                ### Contexto: {{$contexto}} ###END### 
                
                
                
                
                8) Instrucciones expeciales:
                    # El cliente entiende que hay una conversacion que continua. Por ejemplo:
                    # Ejecutivo: Hola, tengo un problema con mi telefono
                    # Asistente (tu): Entiendo que tienes un problema con tu telefono. Como puedo ayudarte?
                    # Ejecutivo: Cuanto cuesta roaming en Brazil
                    # Asistente: El costo de roaming en Brazil es de 10 dolares por dia
                    # Ejecutivo: Y cuanto cuesta en Argentina
                    # Asistente: El costo de roaming en Argentina es de 5 dolares por dia
                    # Cual fue mi ultima pregunta?
                    # Asistetente (AI): Tu ultima pregunta fue cuanto cuesta en Argentina
                    Recuerda tu estas contestando el ejecutivo para ayudarle
                9)Importanet no inventes informacion. Usa la historia para contestar. Usa el contexto para contestar
                
                IMPORTANTE:  esta es la pregunta o el problema del cliente usala para contestar y dar una respuesta 
                USA ESTA COMO PREGUNTA!!!!
                {{$input_text}}
                ### END
                            
                """
            
            prompt_template_config = PromptTemplateConfig(
                template=prompt,
                name="chat",
                template_format="semantic-kernel",
                input_variables=[
                    InputVariable(name="input_text", description="The user input", is_required=True),
                    InputVariable(name="history", description="The conversation history", is_required=True),
                    InputVariable(name="contexto", description="The conversation context", is_required=True),
                ],
                execution_settings=execution_settings,
            )
                
            chat_function = kernel.add_function(
                function_name="chat",
                plugin_name="chatPlugin",
                prompt_template_config=prompt_template_config,
            )

            prompt = prompt.encode('latin1').decode('unicode_escape') 
                # Existing code...

            messages = chat_history.messages

            # Extract the content of each message
            contents = [message.content for message in messages] 

            token_count = num_tokens_from_contents_chat(contents)
            contextoTokens =  num_tokens_from_string(contexto)
           
            
            while token_count > prompt_max_tokens and messages:
                messages.pop(0)
            # Process the user message and get an answer
            answer = await kernel.invoke(chat_function, KernelArguments(input_text=input_text, contexto=contexto, history=chat_history))

            # Show the response
            print(f"ChatBot: {answer}") 
            chat_history.add_user_message(input_text)
            chat_history.add_assistant_message("your answer, use it as context of next question" + str(answer))
            chat_history.add_assistant_message_str("Context from manual data. Use it for next question" + str(contexto))
            
            usuario_ultimaPregunta.append(input_text)
             
            return str(answer)
    else:
        return "No se puede contestar la pregunta"

### This function uses the OpenAI GPT-4 model to generate an intent from a user input.
###
###
async def get_intent(user_input: str, pregunta_anterior: str):
    kernel = sk.Kernel()  
   
    service_id = "default" 
    service_id = "aoai_chat_completion"
    
    kernel.add_service(
        AzureChatCompletion(service_id=service_id, deployment_name=deployment,  api_version="2024-05-01-preview",
                            endpoint=azure_end_point, api_key=api_key)
    )
    req_settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
    req_settings.max_tokens = 15000
    req_settings.temperature = 0.0
    req_settings.top_p = 0.8
    
    
     
    prompt = """  
    
        system: 
            # Eres un experto de Telefonica Chile.
            # Contexto: Estas trabajando en el centro de llamadas de Telefonica Chile y recibes una llamada de un cliente que tiene problemas o 
               preguntas sobre el servicio que ofrecemos.
            # Input:
                # El cliente te pregunta algo o tiene un problema que necesita resolver. 
                  {{$user_input}}
            # Instrucciones paso a paso:
                1) Lee el mensaje del cliente y detecta el intento de la pregunta o el problema que tiene.
                2) Usa tu conocimiento de Telefonica Chile para detectar el intento de la pregunta o el problema.
                3) Si el problema o la pregunta tiene que ver con problemas o preguntas de tipo comercial tales como:
                    "No he pagado mi factura", "Quiero cambiar mi plan", "Quiero cancelar mi servicio", 
                    etc. estos son problemas comerciales.
                4) Si el problema o la pregunta tiene que ver con problemas o preguntas de tipo tecnico tales como:
                    "No tengo señal", "Mi internet no funciona", 
                    "Que es roaming", "Que es RSS", "Que es un APN", "Como configuro mi telefono", "No puedo navegar",
                    
                    "no tengo ocbertura", "No puedo navegar" "No puedo hacer llamadas", etc. estos son problemas tecnicos.
            
                5) Detecta el intento de la pregunta o el problema y clasificalo como "ProblemaTecnico" o "ProblemaComercial".
                6) Si el problema detectado es Tecnico.
                    6a) Detecta el tipo de problema tecnico que tiene el cliente y clasificalo en una de las categorias que se 
                        encuentran en esta lista {{$categorias}}
                    6b) Revisa las preguntas anteriores y ajusta la pregunta actual para que tenga contexto de las preguntas anteriores.
                        sigue la logica.
                                    ###START### 
                                    preguntas anteriores lista: {{$pa}}
                                    ###END###
                        Importante: Usa toda las preguntas anteriores para mejorar la pregunta actual. Esto por que es parte de un dialogo
                        entre el ejecutivo y un Large Language Model de AI. OSea que la pregunta actual tiene que tener contexto de la pregunta anterior.
                        hazlo no lo evites.
           
                        Ejemplo: Solo usa como ejemplo las XXXX y YYYY son valores que pueden ser Paises, ciudades, etc. 
                        IMPORTANTE: create la respuesta mejorada basados en la preguntas anteriores. Con esto podemos buscar lo que queremos en Azure AI search. Gracias
                            pregunta 1: Puedo hacer roaming an eBrazil?
                            Respuesta mejorada: Puedo hacer roaming en Brazil?
                            pregunta 2: Puedo hacer roaming en XXX?
                            Respuesta mejorada: Puedo hacer roaming en XXXX?
                            pregunta 3: Puedo hacer roaming en YYYYY?
                            Respuesta mejorada: Puedo hacer roaming en YYYY?
                            pregunta 4: cuantos GB puedo hacer?
                            Respuesta mejorada: Cuantos GB puedo hacer en roamingen YYYY? 
                            pregunta5: como lo activo?
                            Respuesta mejorada: Como activo el roaming en YYYY?
                            
                        
                  7) Asugurate the complementar la pregunta mejorada con la preguntas anteriores aqui 
                
           
                       Instrucccion de como responder:  siempre en JSON no comentarios solo el JSON  
                       Importante: No ocmentarios, sugeremcias, etc solo el JSON
                                    
                           {  
                                "tipo": "pregunta",  
                                "tipo_problema_pregunta": "ProblemaTecnico",  
                                "pregunta_mejorada": "¿Qué es Pasaporte RRS y cuándo expira?",  
                                "categoria": "Roaming"  
                            }  


                        ]  

 
    
    """
    
    prompt_template_config = PromptTemplateConfig(
    template=prompt,
    name="extract",
    template_format="semantic-kernel",
    execution_settings=req_settings,
)
    with open('classifications.txt', 'r') as f:
        content = f.read()
    function = kernel.add_function(
            function_name="extract_problems",
            plugin_name="extract_plugin",
            prompt_template_config=prompt_template_config,
        )
 
    with open('categories.txt', 'r') as f:
        categorias = f.read()
    try:
        result = await kernel.invoke(function, user_input=user_input, pa=pregunta_anterior,
                                     categorias=categorias)
        responseSTR = str(result)

        # Convert result from a string to a list of dictionaries
        result = json.loads(responseSTR)
 

        # Convert result back to a string
       
    except Exception as e:
        response = f"An error occurred: {str(e)}"

    return result
    


   
    

        