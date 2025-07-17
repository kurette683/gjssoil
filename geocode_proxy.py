import os
import json
import requests

def geocode_address(address):
    KAKAO_API_KEY = os.environ.get("KAKAO_API_KEY")
    if not KAKAO_API_KEY:
        return {"error": "KAKAO_API_KEY not set in environment variables"}, 500

    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        if data and data["documents"]:
            # Return the first result's latitude and longitude
            return {
                "latitude": float(data["documents"][0]["y"]),
                "longitude": float(data["documents"][0]["x"])
            }, 200
        else:
            return {"error": "No results found for the given address"}, 404

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}, 500
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}, 500

if __name__ == "__main__":
    # This part is for local testing or direct execution within GitHub Actions
    # In a real GitHub Actions workflow, inputs would come from workflow_dispatch
    # For demonstration, we'll use a dummy address
    # In a real scenario, the address would be passed as an argument or environment variable
    # For example, if triggered by workflow_dispatch, it would be in github.event.inputs
    
    # Example usage (for local testing):
    # result, status_code = geocode_address("광주광역시청")
    # print(json.dumps(result, ensure_ascii=False, indent=4))
    
    # When used in GitHub Actions, the address will be passed as an argument
    # For now, we'll just define the function.
    pass