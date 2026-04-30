import json
import openai
import os  # Import os to read environment variables

# ✅ Set your OpenAI API key
openai.api_key = ""  # Replace with your actual API key

# ✅ Initialize the OpenAI client
client = openai.OpenAI(api_key="")  # 🔥 FIXED: Pass API key explicitly


from collections import defaultdict

products_file = 'products.json'
categories_file = 'categories.json'

delimiter = "####"
step_2_system_message_content = f"""
You will be provided with customer service a conversation. \
The most recent user query will be delimited with \
{delimiter} characters.
Output a python list of objects, where each object has \
the following format:
    'category': <one of parts,engine_parts,braking_system,electrical_system,suspension_steering>,
OR
    'products': <a list of products that must \
    be found in the allowed products below>

Where the categories and products must be found in \
the customer service query.
If a product is mentioned, it must be associated with \
the correct category in the allowed products list below.
If no products or categories are found, output an \
empty list.
Only list products and categories that have not already \
been mentioned and discussed in the earlier parts of \
the conversation.

Allowed products: 

parts category:
Brake Pads
Oil Filter
Spark Plug
adiator Assembly
Air Filter
Clutch Kit
Wiper Blades

engine_parts category:
Piston Ring Set
Timing Belt Kit
Cylinder Head Gasket

braking_system category:
Brake Pads (Front)
Brake Disc Rotor

electrical_system category:
Car Battery (12V 35Ah)
Spark Plug (Iridium)

suspension_steering category:
Shock Absorber (Front)
Steering Rack Assembly

Only output the list of objects, with nothing else.
"""

step_2_system_message = {'role':'system', 'content': step_2_system_message_content}    


step_4_system_message_content = f"""
    You are a customer service assistant for a large spare parts delear. \
    Respond in a friendly and helpful tone, with VERY concise answers. \
    Make sure to ask the user relevant follow-up questions.
"""

step_4_system_message = {'role':'system', 'content': step_4_system_message_content}    

step_6_system_message_content = f"""
    You are an assistant that evaluates whether \
    customer service agent responses sufficiently \
    answer customer questions, and also validates that \
    all the facts the assistant cites from the product \
    information are correct.
    The conversation history, product information, user and customer \
    service agent messages will be delimited by \
    3 backticks, i.e. ```.
    Respond with a Y or N character, with no punctuation:
    Y - if the output sufficiently answers the question \
    AND the response correctly uses product information
    N - otherwise

    Output a single letter only.
"""

step_6_system_message = {'role':'system', 'content': step_6_system_message_content}    

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0, max_tokens=500):
    openai.api_key = ""  # Replace with your actual API key
    client = openai.OpenAI(api_key="")  
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


def create_categories():
    categories_dict = {
      'Billing': [
          'Unsubscribe or upgrade',
          'Add a payment method',
          'Explanation for charge',
          'Dispute a charge'
      ],
      'Technical Support': [
          'General troubleshooting',  # ✅ Comma added
          'Device compatibility',
          'Software updates'
      ],
      'Account Management': [
          'Password reset',  # ✅ Comma added
          'Update personal information',
          'Close account',
          'Account security'
      ],
      'General Inquiry': [
          'Product information',  # ✅ Comma added
          'Pricing',
          'Feedback',
          'Speak to a human'
      ]
    }
    
    with open(categories_file, 'w') as file:
        json.dump(categories_dict, file, indent=4)  # ✅ Pretty print for readability

    return categories_dict

def get_categories():
    with open(categories_file, 'r') as file:
        categories = json.load(file)
    return categories

def get_product_list():
    """
    Used in L4 to get a flat list of products
    """
    products = get_products()  # Ensure `get_products()` function is defined
    return list(products.keys())  # ✅ Simplified loop

def get_products():
    with open(products_file, 'r') as file:
        products = json.load(file)
    return products

def get_products_and_categorys():
    """
    Used in L5
    """
    products = get_products()
    products_by_category = defaultdict(list)
    for product_name, product_info in products.items():
        category = product_info.get('category')
        if category:
            products_by_category[category].append(product_name)
    
    return dict(products_by_category)
    
def find_category_and_product(user_input, products_and_category):
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of JSON objects, where each object has the following format:
        "category": <one of parts,engine_parts,braking_system,electrical_system,suspension_steering>,
    OR
        "products": <a list of products that must be found in the allowed products below>

    Where the categories and products must be found in the customer service query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list.

    The allowed products are provided in JSON format.
    The keys of each item represent the category.
    The values of each item are a list of products that are within that category.
    Allowed products: {products_and_category}
    
    """
    messages = [  
        {"role": "system", "content": system_message},    
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"}
    ] 
    return get_completion_from_messages(messages)

def find_category_and_product_onlys(user_input, products_and_category):
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of objects, where each object has the following format:
    "category": <one of parts,engine_parts,braking_system,electrical_system,suspension_steering>,
    OR
    "products": <a list of products that must be found in the allowed products below>

    Where the categories and products must be found in the customer service query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list. Return in json format

    Allowed products: 
    parts category:
    Brake Pads
    Oil Filter
    Spark Plug
    adiator Assembly
    Air Filter
    Clutch Kit
    Wiper Blades
    
    engine_parts category:
    Piston Ring Set
    Timing Belt Kit
    Cylinder Head Gasket
    
    braking_system category:
    Brake Pads (Front)
    Brake Disc Rotor
    
    electrical_system category:
    Car Battery (12V 35Ah)
    Spark Plug (Iridium)
    
    suspension_steering category:
    Shock Absorber (Front)
    Steering Rack Assembly
    
    Only output the list of objects, nothing else.
    """
    messages = [  
        {"role": "system", "content": system_message},    
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"}
    ] 
    return get_completion_from_messages(messages)
def get_products_from_query(user_msg):
    """
    Code from L5, used in L8
    """
    products_and_category = get_products_and_category()
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of JSON objects, where each object has the following format:
        "category": <one of parts, engine_parts,braking_system,electrical_system,suspension_steering>,
    OR
        "products": <a list of products that must be found in the allowed products below>

    Where the categories and products must be found in the customer service query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list.

    The allowed products are provided in JSON format.
    The keys of each item represent the category.
    The values of each item are a list of products that are within that category.
    Allowed products: {products_and_category}

    """
    
    messages = [  
        {"role": "system", "content": system_message},    
        {"role": "user", "content": f"{delimiter}{user_msg}{delimiter}"}
    ] 
    category_and_product_response = get_completion_from_messages(messages)
    
    return category_and_product_response

# Product lookup (either by category or by product within category)
def get_product_by_name(name):
    products = get_products()
    return products.get(name, None)

def get_products_by_category(category):
    products = get_products()
    return [product for product in products.values() if product.get("category") == category]

def get_mentioned_product_info(data_list):
    """
    Used in L5 and L6
    """
    product_info_l = []

    if not data_list:
        return product_info_l

    for data in data_list:
        try:
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product:
                        product_info_l.append(product)
                    else:
                        print(f"Error: Product '{product_name}' not found")
            elif "category" in data:
                category_products = get_products_by_category(data["category"])
                product_info_l.extend(category_products)
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return product_info_l

def read_string_to_lists(input_string):
    print(input_string)
    if not input_string:
        return None

    try:
        input_string = input_string.replace("'", "\"")  # Convert single quotes to double quotes for valid JSON
        return json.loads(input_string)
    except json.JSONDecodeError:
        print("Error: Invalid JSON string")
        return None

def generate_output_string(data_list):
    output_string = ""

    if not data_list:
        return output_string

    for data in data_list:
        try:
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product:
                        output_string += json.dumps(product, indent=4) + "\n"
                    else:
                        print(f"Error: Product '{product_name}' not found")
            elif "category" in data:
                category_products = get_products_by_category(data["category"])
                for product in category_products:
                    output_string += json.dumps(product, indent=4) + "\n"
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return output_string

# Example usage:
# product_information_for_user_message_1 = generate_output_string(category_and_product_list)
# print(product_information_for_user_message_1)

def answer_user_msg(user_msg,product_info):
    """
    Code from L5, used in L6
    """
    delimiter = "####"
    system_message = f"""
    You are a customer service assistant for a Spare parts delear.\
    Respond in a friendly and helpful tone, with concise answers. \
    Make sure to ask the user relevant follow up questions.
    """
    # user_msg = f"""
    # tell me about the smartx pro phone and the fotosnap camera, the dslr one. Also what tell me about your tvs"""
    messages =  [  
    {'role':'system', 'content': system_message},   
    {'role':'user', 'content': f"{delimiter}{user_msg}{delimiter}"},  
    {'role':'assistant', 'content': f"Relevant product information:\n{product_info}"},   
    ] 
    response = get_completion_from_messages(messages)
    return response

def create_products():
    """
        Create products dictionary and save it to a file named products.json
    """
    # product information
    # fun fact: all these products are fake and were generated by a language model
    products = {
        "Brake Pads": {
            "id": "BP-001",
            "name": "Brake Pads",
            "category": "parts",
            "brand": "Bosch",
            "compatibility": ["Maruti Swift 2018", "Hyundai i20"],
            "price": 1250,
            "stock": 10
        },
        "Oil Filter": {
            "id": "OF-502",
            "name": "Oil Filter",
            "category": "parts",
            "brand": "Purolator",
            "compatibility": ["Honda City", "Toyota Glanza"],
            "price": 450,
            "stock": 25
        },
        "Spark Plug": {
            "id": "SP-101",
            "name": "Spark Plug",
            "category": "parts",
            "brand": "NGK",
            "compatibility": ["Royal Enfield Classic 350", "Bajaj Pulsar"],
            "price": 180,
            "stock": 50
        },
        "Radiator Assembly": {
            "id": "RD-303",
            "name": "Radiator Assembly",
            "category": "parts",
            "brand": "Denso",
            "compatibility": ["Mahindra XUV500", "Tata Safari"],
            "price": 4200,
            "stock": 5
        },
        "Air Filter": {
            "id": "AB-901",
            "name": "Air Filter",
            "category": "parts",
            "brand": "Rockstar",
            "compatibility": ["TVS Apache RTR", "Hero Splendor"],
            "price": 350,
            "stock": 40
        },
        "Clutch Kit": {
            "id": "CL-404",
            "name": "Clutch Kit",
            "category": "parts",
            "brand": "Exedy",
            "compatibility": ["Volkswagen Vento", "Skoda Rapid"],
            "price": 8500,
            "stock": 3
        },
        "Wiper Blades": {
            "id": "WB-202",
            "name": "Wiper Blades",
            "category": "parts",
            "brand": "Michelin",
            "compatibility": ["Universal Fit", "Kia Seltos", "Ford EcoSport"],
            "price": 950,
            "stock": 15
        },
        "Piston Ring Set": {
            "id": "ENG-001",
            "name": "Piston Ring Set",
            "category": "engine_parts",
            "brand": "Mahle",
            "compatibility": ["Maruti Suzuki Swift", "Hyundai i20"],
            "price": 1850,
            "stock": 15
        },
        "Timing Belt Kit": {
            "id": "ENG-002",
            "name": "Timing Belt Kit",
            "category": "engine_parts",
            "brand": "Gates",
            "compatibility": ["Honda City", "Honda Civic"],
            "price": 3200,
            "stock": 8
        },
        "Cylinder Head Gasket": {
            "id": "ENG-003",
            "name": "Cylinder Head Gasket",
            "category": "engine_parts",
            "brand": "Victor Reinz",
            "compatibility": ["Tata Nexon", "Tata Altroz"],
            "price": 950,
            "stock": 20
        },
        "Brake Pads (Front)": {
            "id": "BRK-001",
            "name": "Brake Pads (Front)",
            "category": "braking_system",
            "brand": "Bosch",
            "compatibility": ["Maruti Suzuki Swift", "Hyundai i20", "Kia Seltos"],
            "price": 1250,
            "stock": 30
        },
        "Brake Disc Rotor": {
            "id": "BRK-002",
            "name": "Brake Disc Rotor",
            "category": "braking_system",
            "brand": "Brembo",
            "compatibility": ["Hyundai Creta", "Kia Seltos"],
            "price": 2800,
            "stock": 12
        },
        "Car Battery (12V 35Ah)": {
            "id": "ELE-001",
            "name": "Car Battery (12V 35Ah)",
            "category": "electrical_system",
            "brand": "Exide",
            "compatibility": ["Maruti Suzuki Swift", "Hyundai Grand i10"],
            "price": 3800,
            "stock": 6
        },
        "Spark Plug (Iridium)": {
            "id": "ELE-002",
            "name": "Spark Plug (Iridium)",
            "category": "electrical_system",
            "brand": "NGK",
            "compatibility": ["Honda City", "Toyota Corolla"],
            "price": 450,
            "stock": 40
        },
        "Shock Absorber (Front)": {
            "id": "SUS-001",
            "name": "Shock Absorber (Front)",
            "category": "suspension_steering",
            "brand": "Monroe",
            "compatibility": ["Hyundai Creta", "Kia Seltos"],
            "price": 2100,
            "stock": 10
        },
        "Steering Rack Assembly": {
            "id": "SUS-002",
            "name": "Steering Rack Assembly",
            "category": "suspension_steering",
            "brand": "Mando",
            "compatibility": ["Tata Nexon"],
            "price": 8900,
            "stock": 2
        }
    }

    products_file = 'products.json'
    with open(products_file, 'w') as file:
        json.dump(products, file)
        
    return products


from collections import defaultdict
import json

def get_products_and_category():
    """
    Retrieves product details and categorizes them properly.
    Ensures all categories exist even if they have no products.
    """
    predefined_categories = [
        "parts", "engine_parts",
        "braking_system", "electrical_system",
        "suspension_steering"
    ]

    try:
        products = get_products()  # Ensure this function is defined and returns a dictionary
        if not isinstance(products, dict):
            raise ValueError("get_products() did not return a valid dictionary.")

        products_by_category = defaultdict(list)

        # Add existing products to their categories
        for product_name, product_info in products.items():
            category = product_info.get('category', None)
            if category:
                products_by_category[category].append(product_name)

        # Ensure all predefined categories exist (even if empty)
        for category in predefined_categories:
            if category not in products_by_category:
                products_by_category[category] = []

        return dict(products_by_category)

    except Exception as e:
        print(f"Error in get_products_and_category: {e}")
        return {category: [] for category in predefined_categories}  # Return empty categories


def find_category_and_product_only(user_input, products_and_category):
    """
    Uses LLM to extract categories and products.
    """
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The query will be enclosed within {delimiter} characters.
    
    Extract both category and products from the query.
    
    **Output Format:**
    A JSON list of objects where each object has:
    - "category": (one of the predefined categories)
    - "products": (a list of extracted product names from the predefined list)

    **Rules:**
    - If a category is mentioned but no products, return an empty product list for that category.
    - If a product is mentioned, ensure it's mapped to the correct category.
    - If no relevant information is found, return an empty list `[]`.
    
    **Predefined Categories & Products:**
    {json.dumps(products_and_category, indent=4)}
    
    Only return the JSON list. No extra text.
    """

    messages = [  
        {"role": "system", "content": system_message},    
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"}
    ] 

    return get_completion_from_messages(messages)


def read_string_to_list(input_string):
    """
    Converts a JSON string to a Python list.
    Handles cases where the input may be malformed or empty.
    """
    if not input_string:
        return []
    try:
        input_string = input_string.replace("```json", "").replace("```", "").strip()  # Remove code block markers if present
        return json.loads(input_string)
    except json.JSONDecodeError:
        print("Error: Invalid JSON string")
        return []
