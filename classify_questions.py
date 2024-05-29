import pandas as pd
import OpenAIKernel as oai
from azure.core.exceptions import ResourceNotFoundError

import Gen2Services as g2s
import DocumentAnalysis as da 
import OpenAIKernel as oai 
import json
from dotenv import load_dotenv
import os
import collections
import Tools as tools 
async def extract_problema_column(file_path):
    
# 
    connection_string = os.getenv('CONNECTION_STRING')
  # This function reads a CSV file into a DataFrame, extracts problem-solution pairs, classifies the problems 
  # in batches, converts the results to JSON, and uploads the JSON to a DataLake.
    df = pd.read_csv(file_path, encoding='ISO-8859-1')
    problema_column = df['problema']
    solucion_column = df['solucion']
    problem_solution_pairs = [{'problem'+str(i+1): p, 'solution': s} for i, (p, s) in enumerate(zip(problema_column, solucion_column))]
    for i in range(0, len(problem_solution_pairs), 5):
        try:
            batch = problem_solution_pairs[i:i+5]
            result =  await oai.classify_problem(batch)
            data = json.loads(result)  
            json_data_QA = json.dumps(data) 
            # Upload the JSON string to the DataLake
            g2s.upload_to_datalake(connection_string, "telefonicadata/KBDEV/ProblemasSoluciones", "TransformedQATest" + str(i) + ".json", json_data_QA) 
        except json.JSONDecodeError:
            print(f"An error occurred when processing batch {i}. Skipping this batch.")
        continue
    return problem_solution_pairs

 ##This function merges multiple JSON files from a specified file system 
 # into a single JSON file. It downloads files with a common prefix and a number in their
 # names, combines their data, and writes the combined data to a new file.
def merge_files(file_system_name, file_prefix, file_count):
    merged_data = []
    connection_string = os.getenv('CONNECTION_STRING')
    for i in range(0, file_count, 5):
        file_path = f"{file_prefix}{i}.json"
        try:
            file_data = g2s.download_content_as_json(connection_string, file_system_name, file_path)
            merged_data.extend(file_data)
        except ResourceNotFoundError:
            print(f"File {file_path} not found. Skipping.")

    with open('C:/Data/Telefonica/merged_file.json', 'w') as f:
      json.dump(merged_data, f)

# This function downloads a JSON file, counts the occurrences of each category in the file, 
# sorts the categories, and writes the sorted category counts to a new JSON file.
def SummaryCategory():
    connection_string = os.getenv('CONNECTION_STRING')
    file_data = g2s.download_content_as_json(connection_string, "telefonicadata", "KBDEV/Silver/TransformedQA.json")
    
    # Prepare categories
    categories = []
    problem_tecnico_count = 0
    for item in file_data:
        if item.get('clasificacion') == 'ProblemaTecnico':
            problem_tecnico_count += 1
            if isinstance(item['category'], list):
                categories.extend(item['category'])
            else:
                categories.append(item['category'])

    # Count the categories
    category_counts = collections.Counter(categories)

    # Sort by category name
     
    sorted_category_counts = dict(sorted(category_counts.items(), key=lambda item: item[1], reverse=True))

    print(f'Total ProblemaTecnico: {problem_tecnico_count}')

    # Write the result to a new JSON file
    with open('C:/Data/Telefonica/category_summary_tecnical.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_category_counts, f, ensure_ascii=False)
        
def GroupSummary():
    connection_string = os.getenv('CONNECTION_STRING')
    file_data = g2s.download_content_as_json(connection_string, "telefonicadata", "KBDEV/Silver/TransformedQA.json")  
  
    # Group dictionary where each key is a group name and each value is a list of related issues  
    issues_by_group = {  
    "Network Issues": [  
        "Problemas de red movil",  
        "Internet Movil",  
        "Problemas de conexión red móvil",  
        "Cobertura",  
        "Falta Cobertura",  
        "Problemas de coneccion red movil",  
        "Problemas de red móvil",  
        "Conexion 3G, Conexion 4G, Conexion 5G",  
        "Problemas de señal",  
        "Problemas de cobertura",  
        "Problemas de conexión a la red móvil",  
        "Problemas de red",  
        "Problemas con la señal de telefonía móvil",  
        "Problemas de red movil, Problemas de coneccion red movil",  
        "Problemas de red móvil, Problemas de conexión red móvil",  
        "Problemas de cobertura, Problemas de internet",  
        "Problemas de señal y servicio",  
        "No Navega, Problemas de red movil",  
        "Problemas de red movil, Internet caido",  
    ],  
    "Internet Connectivity": [  
        "Internet Casa",  
        "Problemas de conexión a internet",  
        "No Navega",  
        "Internet caido",  
        "Conexion 5G",  
        "Conexion 3G, Conexion 4G, Conexion 5G",  
        "Problemas de velocidad de internet",  
        "Internet caido, Problemas de coneccion red movil",  
        "Internet Casa, Problemas de conexion red movil",  
        "Problemas de conexión a internet móvil",  
        "Internet Casa, Internet Movil",  
        "Problemas con la conexión a internet",  
        "Problemas con el servicio de internet",  
        "Internet en casa",  
        "Conexion 3G, Conexion 4G, Internet Movil",  
        "Conexion 4G, Internet Casa",  
        "Internet caído",  
        "Internet Movil, Facturacion",  
    ],  
    "Telephone Line Issues": [  
        "Linea Telefonica fija",  
        "Telefono perdido",  
        "No puede llamar o recibir llamadas",  
        "Telefono desconectado",  
        "No puede enviar or recibir SMS",  
        "No puede enviar o recibir SMS",  
        "Problemas de llamadas",  
        "Problemas con la línea telefónica",  
        "Problemas de línea móvil",  
    ],  
    "Billing and Charges": [  
        "Facturacion",  
        "Facturación",  
        "Movistar TV, Facturacion",  
        "Internet Casa, Facturacion",  
        "Problemas de facturación de servicios de terceros",  
        "Facturacion, Configuracion Smartphone",  
        "Facturacion, Linea Telefonica fija",  
        "Conexion 4G, Facturacion",  
        "Facturacion, Internet Casa",  
        "Roaming, Facturacion",  
    ],  
    "Mobile Services": [  
        "Configuracion Smartphone",  
        "SIMCARD",  
        "Roaming Activacion",  
        "Roaming",  
        "Configuración de dispositivos",  
        "Configuración Smartphone",  
    ],  
    "Television Services": [  
        "Movistar TV",  
        "Problemas con el servicio de televisión",  
        "Problemas de televisión"  
    ]  
}  
    issue_to_group = {issue: group for group, issues in issues_by_group.items() for issue in issues}  
        
    # Prepare categories and count  
    categories = []  
    problem_tecnico_count = 0  
    
    # A new list to hold only the 'ProblemaTecnico' items with the added 'group' field  
    filtered_file_data = []  
    
    # Filtering file_data and updating the new list  
    for item in file_data:  
        # Check for 'ProblemaTecnico' classification  
        if item.get('clasificacion') == 'ProblemaTecnico':  
            problem_tecnico_count += 1  
            # Check if 'category' is a list or a single value and append/extend accordingly  
            if isinstance(item.get('category'), list):  
                categories.extend(item['category'])  
            else:  
                categories.append(item['category'])  
            
            # Assuming 'category' is the field in your items that contains the issue  
            category = item.get('category')  
            if category:  
                # If the category exists and is not a list, find the group and add it to the item  
                if isinstance(category, list):  
                    # If category is a list, you may want to handle multiple categories per item differently  
                    # For simplicity, let's just take the first category in the list for this example  
                    category = category[0]  
                group = issue_to_group.get(category, "Other")  # Default to "Other" if no match is found  
                item['group'] = group  
            
            # Add the item to the filtered list  
            filtered_file_data.append(item)  
    
    # At this point, filtered_file_data contains only items with 'ProblemaTecnico' and the added 'group'  
    # You can print it out, save it, or perform other operations as needed  
    
    # Example: print out the filtered items  
     
    with open('C:/Data/Telefonica/group_summary_tecnical.json', 'w', encoding='utf-8') as f:
            json.dump(filtered_file_data, f, ensure_ascii=False)
  
        