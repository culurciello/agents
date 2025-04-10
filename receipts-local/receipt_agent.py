from PIL import Image
import pandas as pd
import base64
from io import BytesIO
from pathlib import Path
import ollama

class ReceiptProcessorAgent:
    def __init__(self):
        pass
        
    def process_receipt_image(self, image_path):
        """Process an image using Ollama's vision model"""

        # Open and convert image to base64
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            response = ollama.chat(
                model='llama3.2-vision',
                messages=[{
                    'role': 'user',
                    'content': 'Extract the following information from this receipt: date, total amount, vendor name, and items purchased. Format as JSON. Only provide the JSON as response, nothing else',
                    'images': [img_str]
                }]
            )

        return response['message']['content']

class DataWriterAgent:
    def __init__(self):
        pass

    def process_data(self, response_in):
        prompt = f"Make sure the data in {response_in} is in the following JSON format: date, total amount, vendor name, and items purchased. If not, correct it. Only provide the JSON as response, nothing else"
        response = ollama.generate('llama3.2', prompt)['response']
        return response



def save_to_csv(results, output_dir='.'):
    """Save all receipt data to a single CSV file in the specified directory.
    
    Args:
        results: List of tuples (image_name, json_data)
        output_dir: Directory to save the CSV file
    """
    import json
    import os
    from datetime import datetime

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Create a list to store all receipt data
        all_data = []
        
        # Process each receipt
        for image_name, json_str in results:
            receipt_data = json.loads(json_str)
            receipt_dict = {
                'Image': image_name,
                'Date': receipt_data.get('date', ''),
                'Vendor': receipt_data.get('vendor_name', ''),
                'Total Amount': receipt_data.get('total_amount', ''),
                'Items': ', '.join(receipt_data.get('items_purchased', []))
            }
            all_data.append(receipt_dict)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        filename = os.path.join(output_dir, f'receipts.csv')
        
        # Save to CSV
        df.to_csv(filename, index=False)
        return filename
    except Exception as e:
        print(f"Error saving receipt data: {e}")
        return None


def main():

    # agents:
    processor = ReceiptProcessorAgent()
    writer = DataWriterAgent()

    receipt_path = Path('receipts')
    results = []
    for image_file in receipt_path.glob('*'):
        if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            print(f"Processing {image_file.name}...")
            response = processor.process_receipt_image(image_file)
            # response = """{"date": "Fri 04/07/2017", "total amount": "$12.00", "vendor name": "Main Street Restaurant", "items purchased": ["Chocolate Chip Cookie", "Apple Pie", "Lava Cake"]}"""            
            # print("PROCESSOR RESPONSE:", response)
            writer_response = writer.process_data(response)
            # print("WRITER RESPONSE", writer_response)
            print(image_file.name, writer_response)
            results.append((image_file.name, writer_response))

    # Save the processed data to CSV
    saved_file = save_to_csv(results)

if __name__ == "__main__":
    main()
