import pandas as pd
import requests
import json
import time

def generate_gjssoil_data():
    """
    gjssoil_info.csv의 UNI_ID를 바탕으로 오피넷 API에서 가격 정보를 조회하고
    gjssoil_data.json 및 gjssoil_data.csv로 저장합니다.
    """
    input_info_path = "gjssoil_info.csv"
    output_json_path = "gjssoil_data.json"
    output_csv_path = "gjssoil_data.csv"
    opinet_api_key = "F250708581" # 여기에 실제 오피넷 API 키를 입력해야 합니다.

    print(f"'{input_info_path}' 파일 읽는 중...\n")
    try:
        df_info = pd.read_csv(input_info_path, encoding="utf-8-sig")
        print(f"총 {len(df_info)}개의 주유소 상세 정보 로드 완료.\n")
    except FileNotFoundError:
        print(f"오류: '{input_info_path}' 파일을 찾을 수 없습니다. 먼저 get_more_stn_info.py를 실행하여 생성해주세요.")
        return
    except Exception as e:
        print(f"CSV 파일 읽기 중 오류 발생: {e}")
        return

    processed_stores = []
    
    def fetch_price_by_id(uni_id):
        url = "http://www.opinet.co.kr/api/detailById.do"
        params = {
            "code": opinet_api_key,
            "out": "json",
            "id": uni_id
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            prices = {}
            oil_list = data.get("RESULT", {}).get("OIL")
            if not oil_list:
                print(f"경고: UNI_ID '{uni_id}'에 대한 OIL 정보가 없습니다. 응답: {data}")
                return {}
            oil_prices_list = oil_list[0].get("OIL_PRICE")
            if oil_prices_list:
                for oil in oil_prices_list:
                    prod_cd = oil.get("PRODCD")
                    price = oil.get("PRICE")
                    if prod_cd and price is not None:
                        prices[prod_cd] = price
                return prices
            else:
                print(f"경고: UNI_ID '{uni_id}'에 대한 OIL_PRICE 정보가 없습니다. 응답: {data}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"가격 정보 조회 실패 (UNI_ID '{uni_id}'): {e}")
            return {}
        except (ValueError, IndexError) as e:
            print(f"데이터 처리 중 오류 발생 (UNI_ID '{uni_id}'): {e}. 응답: {data}")
            return {}

    print("오피넷 API를 통해 가격 정보 수집 중...\n")
    for index, row in df_info.iterrows():
        uni_id = row["UNI_ID"]
        store_name = row["OS_NM"]
        address = row["NEW_ADR"]
        category = row["POLL_DIV_CD"]
        gis_x = row["GIS_X_COOR"]
        gis_y = row["GIS_Y_COOR"]

        prices_from_api = fetch_price_by_id(uni_id)
        
        processed_stores.append({
            "OS_NM": store_name,
            "NEW_ADR": address,
            "POLL_DIV_CD": category,
            "GIS_X_COOR": gis_x,
            "GIS_Y_COOR": gis_y,
            "prices": prices_from_api,
            "UNI_ID": uni_id
        })
        time.sleep(0.1) # API 호출 간격 조절

    print(f"총 {len(processed_stores)}개의 업체 정보에 가격 정보 추가 완료.\n")

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(processed_stores, f, ensure_ascii=False, indent=4)
    print(f"처리된 데이터가 '{output_json_path}' 파일로 저장되었습니다.\n")

    if processed_stores:
        flat_data = []
        for store in processed_stores:
            flat_store = {
                "OS_NM": store["OS_NM"],
                "NEW_ADR": store["NEW_ADR"],
                "POLL_DIV_CD": store["POLL_DIV_CD"],
                "GIS_X_COOR": store["GIS_X_COOR"],
                "GIS_Y_COOR": store["GIS_Y_COOR"],
                "PRICE_B027": store["prices"].get("B027"),
                "PRICE_D047": store["prices"].get("D047"),
                "PRICE_K015": store["prices"].get("K015"),
                "PRICE_B034": store["prices"].get("B034"),
                "PRICE_C004": store["prices"].get("C004"),
                "UNI_ID": store["UNI_ID"]
            }
            flat_data.append(flat_store)
        
        df_output = pd.DataFrame(flat_data)
        df_output.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
        print(f"처리된 데이터가 '{output_csv_path}' 파일로 저장되었습니다.\n")
    else:
        print("수집된 데이터가 없어 CSV 파일을 생성하지 않습니다.")

if __name__ == "__main__":
    generate_gjssoil_data()