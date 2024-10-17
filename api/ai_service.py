import openai
import os
import json

from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from dotenv import load_dotenv


def format_bundles(text):
    """
    Convert the text response from OpenAI into a list of bundles.

    Args:
        text (str): The response text from OpenAI.

    Returns:
        list of dict: Bundles with product details.
    """
    try:
        # Attempt to parse the JSON response
        bundles = json.loads(text)
        # Validate and return bundles if they conform to the expected format
        if isinstance(bundles, list) and all(
                isinstance(bundle, dict) and 'bundle_name' in bundle and 'products' in bundle
                for bundle in bundles
        ):
            # Ensure that each product in the bundle contains only 'id' and 'name'
            for bundle in bundles:
                if not all('id' in product and 'name' in product for product in bundle['products']):
                    return {'error': 'Invalid product format in bundle'}
            return bundles
        else:
            return {'error': 'Invalid response format'}
    except json.JSONDecodeError:
        # Handle any errors in parsing
        return {'error': 'Failed to parse JSON response'}


class ProductBundleGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        llm = OpenAI(model="gpt-4-1106-preview")
        self.service_context = ServiceContext.from_defaults(llm=llm)

    def generate_bundles(self, products_data, max_retries=3):
        # Create a .txt file that contains the products_data
        with open('api/media/products_data.txt', 'w') as file:
            json.dump(products_data, file, indent=4)

        # Load documents from the .txt file
        documents = SimpleDirectoryReader('api/media').load_data()

        # Create the vector store index from the loaded documents
        index = VectorStoreIndex.from_documents(documents, service_context=self.service_context)
        query_engine = index.as_query_engine()

        # Create a prompt for generating a suggestion of product bundles (max of 3)
        my_prompt = (
            "Given the following products, suggest up to 3 product bundles that would "
            "provide a good mix and maximize value for the customer. Each bundle should be "
            "formatted as a JSON object with the following structure:\n"
            "[\n"
            "  {\n"
            "    \"bundle_name\": \"<Name of the bundle>\",\n"
            "    \"products\": [\n"
            "      {\n"
            "        \"id\": <Product ID>,\n"
            "        \"name\": \"<Product Name>\"\n"
            "      },\n"
            "      ...\n"
            "    ]\n"
            "  },\n"
            "  ...\n"
            "]\n\n"
            f"Here is the product data:\n{products_data}\n\
            Respond only with the output in the exact format specified, with no explanation or conversation or other text that wraps it or says it is a json.\n \
            Do not wrap it with ```json ``` or ```json\n```'"
        )

        retry_count = 0
        while retry_count < max_retries:
            # Query the index to generate bundle suggestions
            raw_response = query_engine.query(my_prompt)
            str_response = str(raw_response)

            print(str_response)

            bundles = format_bundles(str_response)

            # Check if formatting was successful
            if 'error' in bundles:
                retry_count += 1
                print(f"Attempt {retry_count} failed: {bundles['error']}. Retrying...")
            else:
                return bundles

        # If the loop exits, it means max_retries was reached
        return {'error': 'Failed to generate bundles in the correct format after multiple attempts'}
