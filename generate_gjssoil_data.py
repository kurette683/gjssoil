import pandas as pd
import requests
import json
import time

def generate_gjssoil_data():
    input_csv_path = "gjssoil_stores.csv"
    output_json_path = "gjssoil_data.json"
    opinet_api_key = "F250708581" # 여기에 실제 오피넷 API 키를 입력해야 합니다.

    print(f"'{input_csv_path}' 파일 읽는 중...")
    try:
        df = pd.read_csv(input_csv_path, encoding="utf-8-sig")
        print(f"총 {len(df)}개의 업체 정보 로드 완료.")
    except FileNotFoundError:
        print(f"오류: '{input_csv_path}' 파일을 찾을 수 없습니다. 먼저 CSV 파일을 생성해주세요.")
        return
    except Exception as e:
        print(f"CSV 파일 읽기 중 오류 발생: {e}")
        return

    processed_stores = []
    
    # 오피넷 API 호출 함수
    def fetch_price(store_name):
        url = f"https://www.opinet.co.kr/api/searchByName.do?code={opinet_api_key}&out=json&osnm={store_name}"
        try:
            response = requests.get(url, timeout=5) # 타임아웃 설정
            response.raise_for_status() # HTTP 오류 발생 시 예외 발생
            data = response.json()
            
            if data.get("RESULT", {}).get("OIL_PRICE"):
                prices = {}
                for oil in data["RESULT"]["OIL_PRICE"]:
                    prices[oil["PRODCD"]] = oil["PRICE"]
                return prices
            return {}
        except requests.exceptions.RequestException as e:
            print(f"가격 정보 조회 실패 ({store_name}): {e}")
            return {}

    print("오피넷 API를 통해 가격 정보 수집 중...")
    for index, row in df.iterrows():
        store_name = row["업체명"]
        address = row["업체주소"]
        category = row["업종명"] # 업종명도 포함

        prices = fetch_price(store_name)
        
        processed_stores.append({
            "name": store_name,
            "address": address,
            "category": category,
            "prices": prices # 휘발유, 경유, LPG 가격 포함
        })
        time.sleep(0.1) # API 호출 간격 조절 (과도한 요청 방지)

    print(f"총 {len(processed_stores)}개의 업체 정보에 가격 정보 추가 완료.")

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(processed_stores, f, ensure_ascii=False, indent=4)
    print(f"처리된 데이터가 '{output_json_path}' 파일로 저장되었습니다.")

if __name__ == "__main__":
    generate_gjssoil_data()