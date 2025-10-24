from typing import Any, Dict


def success_response(data: Any) -> Dict[str, Any]:
    """
    Standardize API responses to {status: "success", data: {...}}
    """
    return {
        "status": "success",
        "data": data
    }
