import subprocess
import json
from schemas import DamageCalcRequest

def run_vgc_calculation(request: DamageCalcRequest) -> str:
    """Passes the AI's data to the official Smogon JS calculator."""
    
    # Convert the AI's Pydantic model into a raw JSON string
    payload = request.model_dump_json()
    
    try:
        # Run the Node.js script
        # Note: Ensure the path to calc_bridge.js is correct relative to where you start Uvicorn
        result = subprocess.run(
            ["node", "damage_calc/calc_bridge.js", payload], # If this fails, try "backend/calc_bridge.js"
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip()
        return f"Error running calculator: {error_msg}. Tell the user the calculation failed."
    except FileNotFoundError:
        return "Error: Node.js is not installed or the bridge file is missing."