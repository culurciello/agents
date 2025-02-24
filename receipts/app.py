import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image

st.set_page_config(layout="wide", page_title="Receipt Viewer")

def load_image(image_path):
    return Image.open(image_path)

def main():
    st.title("Receipt Viewer")

    # Load the CSV data
    csv_path = Path('receipts.csv')
    if not csv_path.exists():
        st.warning("receipts.csv not found. Please run receipt_agent.py first to process receipts.")
        return

    try:
        # Load all data
        df = pd.read_csv(csv_path)
        
        # Display all receipts
        for _, receipt_data in df.iterrows():
            # Create a container for each receipt
            with st.container():
                st.markdown("---")  # Separator between receipts
                
                # Create two columns for this receipt
                col1, col2 = st.columns(2)
                
                # Display the receipt data
                with col1:
                    # Create a more readable format for display
                    display_df = pd.DataFrame({
                        'Field': ['Date', 'Vendor', 'Total Amount', 'Items'],
                        'Value': [
                            receipt_data['Date'],
                            receipt_data['Vendor'],
                            receipt_data['Total Amount'],
                            receipt_data['Items']
                        ]
                    })
                    st.subheader(f"Receipt Data: {receipt_data['Vendor']}")
                    st.table(display_df)

                # Display the image
                with col2:
                    image_path = Path('receipts') / receipt_data['Image']
                    try:
                        st.image(load_image(image_path), use_column_width=True)
                    except Exception as e:
                        st.error(f"Error loading image {receipt_data['Image']}: {e}")

    except Exception as e:
        st.error(f"Error reading data: {e}")

if __name__ == "__main__":
    main()
