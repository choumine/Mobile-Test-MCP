from .common import app
from typing import List, Dict, Any
import json


@app.tool()
async def tool_execute_test(test_steps: List[Dict[str, Any]]) -> str:
    """
    Execute user-specified test steps and generate prompts for LLM to follow step by step.
    Each step includes before and after screenshots, with coordinate marking for tap steps.
    
    When user says "start testing", this tool should be invoked to generate execution prompts.
    
    Returns:
        str: Prompt for LLM to execute the test steps
    """
    
    # Generate prompt for LLM
    prompt = "Please execute the test steps:\n\n"
    
    prompt += """
    Execution process:
    1. For each test step:
       - Take a screenshot before execution (xxx_before.png)
       - If it's a tap step, mark the tap coordinates on the before screenshot
       - Execute the step
       - Take a screenshot after execution (xxx_after.png)
    """
    
    prompt += "After executing all steps, use tool_generate_report() to create a test report with before and after screenshots.\n"
    prompt += "Open the final report."
    
    return prompt