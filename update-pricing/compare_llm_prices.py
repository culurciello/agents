import pandas as pd
import os
from datetime import datetime
import litellm

# os.environ["OPENAI_API_KEY"] = "your-api-key"

# ANSI escape codes for colors
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'


def load_excel_files():
    main_price_sheet = pd.read_excel("test/main_pricing_sheet.xlsx")
    new_price_sheet = pd.read_excel("test/vendor1_pricing_sheet.xlsx")
    return main_price_sheet, new_price_sheet


def compare_items(main_price_sheet, main_header, new_price_sheet, new_header):
    # Get headers from both sheets
    main_headers = main_price_sheet.iloc[main_header]
    new_headers = new_price_sheet.iloc[new_header]
    # print headers:
    print(f"Main sheet header: [{GREEN}{'\t'.join(f'{item}' for item in main_headers)}{RESET}]")
    print(f"New sheet header: [{GREEN}{'\t'.join(f'{item}' for item in new_headers)}{RESET}]")
    headers = [main_headers, new_headers]
    
    # List to store matching rows
    matching_rows = []
    
    for index, main_row in main_price_sheet.iloc[main_header+1:].iterrows():
        matching_new_rows = new_price_sheet[new_price_sheet.iloc[:, 0].astype(str).str.contains(str(main_row.iloc[0]), case=False, na=False)]
        if not matching_new_rows.empty:
            for _, match in matching_new_rows.iterrows():
                # Store both complete rows as dictionaries
                matching_rows.append({
                    'main_row':main_row,
                    'new_row':match,
                })
    return matching_rows, headers


def main():
    try:
        main_price_sheet, new_price_sheet = load_excel_files()

        # Find header rows:
        main_header = 3
        new_header = 3

        matching_rows, headers = compare_items(main_price_sheet, main_header, new_price_sheet, new_header)
        # print(f"\nMatching Rows: {matching_rows}")

        # Print header of main and main match, then header new and new match
        # print("\nMatching Rows:")
        
        for match in matching_rows:
            matches_str = ""
            matches_str += f"Main sheet:\n[{'\t'.join(f'{item}' for item in headers[0])}]\n"
            matches_str += f"[{GREEN}{'\t'.join(f'{item}' for item in match['main_row'])}{RESET}]\n"
            matches_str += f"New sheet:\n[{'\t'.join(f'{item}' for item in headers[1])}]\n"
            matches_str += f"[{GREEN}{'\t'.join(f'{item}' for item in match['new_row'])}{RESET}]\n"
            matches_str += "-" * 50 + "\n"
            print("\nProcessing Matching lines:\n", matches_str)

            # create a llm prompt:
            prompt = f"""
            You are a helpful assistant and are tasked to update a row of an excel sheet with new prices.
            Given that the date today is {datetime.now().strftime('%Y-%m-%d')}, find the appropriate new price in the 'New sheet'. 
            You will update the 'Main sheet' with the new prices from the 'New sheet'.    
            Output in JSON format, no other comment or text. Output JSON as:
            "
                "changed": "true/false",
                "updated_main_sheet_row": "[item1, item2, item3, ...]"
            "
            Input rows: {matches_str}. Your response...
            """
            
            # print('Prompt:', prompt)

            # run on ollama
            # response = litellm.completion(
            #     model="ollama/llama3.1:8b-instruct-q4_0", 
            #     messages=[{"role": "user", "content": prompt}],
            #     api_base="http://localhost:11434"
            # )

            # openai call
            response = litellm.completion(
                model = "gpt-4o", 
                messages=[{ "content": prompt,"role": "user"}]
            )
            
            updated_main_row = response.choices[0].message.content    
            print("Updated Main Row:\n", updated_main_row)
            print("-" * 50)
            # input("Press Enter to continue...")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
