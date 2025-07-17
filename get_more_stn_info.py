import pandas as pd
import requests
import time
import json

def get_more_station_info():
    """
    gjssoil_list.csv의 상호 목록을 바탕으로 오피넷 API에서 상세 정보를 조회하고 CSV로 저장합니다.
    """
    input_list_path = "D:\Vault\gemini\gjssoil\gjssoil_list.csv"
    output_filename = "gjssoil_info.csv"
    opinet_api_key = "F250708581" # 여기에 실제 오피넷 API 키를 입력해야 합니다.

    # 광주광역시 시도 코드 및 시군구 코드 (필터링용)
    SIDO_CODE = "16"
    GWANGJU_SIGUNCD = ["1601", "1602", "1603", "1604", "1605"] # 동구, 서구, 북구, 광산구, 남구

    print(f"'{input_list_path}' 파일 읽는 중...")
    try:
        df_list = pd.read_csv(input_list_path, encoding="utf-8-sig")
        print(f"총 {len(df_list)}개의 상호 정보 로드 완료.")
    except FileNotFoundError:
        print(f"오류: '{input_list_path}' 파일을 찾을 수 없습니다. 먼저 matching_stn_info.py를 실행하여 생성해주세요.")
        return
    except Exception as e:
        print(f"CSV 파일 읽기 중 오류 발생: {e}")
        return

    all_station_info = []
    
    print("오피넷 API를 통해 상세 정보 수집 중...")
    for index, row in df_list.iterrows():
        store_name = row["OS_NM"] # gjssoil_list.csv에는 OS_NM 컬럼이 있다고 가정

        url = "http://www.opinet.co.kr/api/searchByName.do"
        params = {
            "code": opinet_api_key,
            "out": "json",
            "osnm": store_name,
            "area": SIDO_CODE # 광주광역시로 검색 범위 제한
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("RESULT", {}).get("OIL"):
                found_stations = json_data["RESULT"]["OIL"]
                
                # 광주광역시 내의 주유소만 필터링 (SIGUNCD 기준)
                gwangju_stations = [
                    s for s in found_stations if s.get("SIGUNCD") in GWANGJU_SIGUNCD
                ]

                if gwangju_stations:
                    # 매칭된 첫 번째 광주 지역 주유소 정보 사용
                    station = gwangju_stations[0] 
                    all_station_info.append({
                        "UNI_ID": station.get("UNI_ID", ""),
                        "POLL_DIV_CD": station.get("POLL_DIV_CD", ""),
                        "OS_NM": station.get("OS_NM", ""),
                        "NEW_ADR": station.get("NEW_ADR", ""),
                        "SIGUNCD": station.get("SIGUNCD", ""),
                        "LPG_YN": station.get("LPG_YN", ""),
                        "GIS_X_COOR": station.get("GIS_X_COOR", ""),
                        "GIS_Y_COOR": station.get("GIS_Y_COOR", "")
                    })
                else:
                    print(f"경고: '{store_name}'에 대해 광주 지역 주유소 상세 정보를 찾을 수 없습니다. 응답: {json_data}")
            else:
                print(f"경고: '{store_name}'에 대한 오피넷 상세 정보가 없습니다. 응답: {json_data}")

        except requests.exceptions.RequestException as e:
            print(f"API 요청 중 오류 발생 ('{store_name}'): {e}")
        
        time.sleep(0.5) # API 호출 간격 조절

    if all_station_info:
        df_output = pd.DataFrame(all_station_info)
        df_output.drop_duplicates(subset=["UNI_ID"], inplace=True) # UNI_ID 기준으로 중복 제거
        df_output.to_csv(output_filename, index=False, encoding="utf-8-sig")
        print(f"\n총 {len(df_output)}개의 주유소 상세 정보가 '{output_filename}' 파일로 저장되었습니다.")
    else:
        print("\n수집된 주유소 상세 정보가 없습니다.")

if __name__ == "__main__":
    get_more_station_info()
