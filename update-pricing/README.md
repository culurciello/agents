# update pricing sheet with AI / LLMs

This is an example of how to update pricing sheets using AI / LLMs.
The idea is that there is a reseller keeping a main pricing sheet and a vendor pricing sheet.
The vendor pricing sheet is updated by the vendor and the reseller needs to update the main pricing sheet.
AI and LLM are to do the work.

## Usage

```
python compare_llm_prices.py 
```

## OpenAI:
works:


euge@Pora-2:~/Desktop/update-pricing $ python compare_llm_prices.py 
Main sheet header: [Product	UOM	vendor price	margin %	sale price]
New sheet header: [Product	UOM	vendor price	notes]

Processing Matching lines:
 Main sheet:
[Product	UOM	vendor price	margin %	sale price]
[vehicular gas 11	gallon	42	15	48.3]
New sheet:
[Product	UOM	vendor price	notes]
[vehicular gas 11	gallon	45	updated 3/2025]
--------------------------------------------------

Updated Main Row:
 ```json
{
    "changed": "true",
    "updated_main_sheet_row": ["vehicular gas 11", "gallon", "45", "15", "51.75"]
}
```
--------------------------------------------------

Processing Matching lines:
 Main sheet:
[Product	UOM	vendor price	margin %	sale price]
[oil motor 33	gallon	33	15	37.95]
New sheet:
[Product	UOM	vendor price	notes]
[oil motor 33	gallon	33	nan]
--------------------------------------------------

Updated Main Row:
 ```json
{
    "changed": "false",
    "updated_main_sheet_row": ["oil motor 33", "gallon", 33, 15, 37.95]
}
```
--------------------------------------------------

Processing Matching lines:
 Main sheet:
[Product	UOM	vendor price	margin %	sale price]
[transmittion fluid 45	gallon	22	15	25.3]
New sheet:
[Product	UOM	vendor price	notes]
[transmittion fluid 45	gallon	22	nan]
--------------------------------------------------

Updated Main Row:
 ```json
{
    "changed": "false",
    "updated_main_sheet_row": ["transmittion fluid 45", "gallon", "22", "15", "25.3"]
}
```




## Ollama: 

results not great often confused on output format and if changed/ not


