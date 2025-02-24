#!/usr/bin/env python
import warnings
from crew_test_openai.crew import CrewTest

def run():
    """
    Run the crew.
    """
    inputs = {
        'receipts_path': 'knowledge/receipts',
        # 'current_year': str(datetime.now().year)
    }
    
    try:
        CrewTest().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")