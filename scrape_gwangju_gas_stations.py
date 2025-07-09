import time
import math
import pandas as pd
import requests

def scrape_gwangju_gas_stations():
    """
    광주광역시청 웹사이트에서 상생카드 가맹 주유소 목록을 스크래핑하여 CSV 파일로 저장합니다.
    """
    all_stores = []
    page_size = 10 # 한 페이지당 결과 수 (응답 JSON의 recordCnt와 일치)
    current_page = 1
    total_pages = 1 # 초기값, 첫 요청 후 업데이트

    # 필터링할 업종명 목록
    ALLOWED_CATEGORIES = [
        "E1가스충전소", "GS가스충전호", "GS주유소", "L P G", "SK가스충전소",
        "SK주유소", "쌍용S-oil가스충전소", "쌍용S-oil주유소", "주 유 소",
        "현대정유가스충전소", "현대정유오일뱅크"
    ]

    print("광주광역시청 웹사이트에서 주유소 정보를 수집합니다...")

    while current_page <= total_pages:
        url = "https://www.gwangju.go.kr/pg/getGjCardList.do"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Referer": "https://www.gwangju.go.kr/economy/contentsView.do?pageId=economy129",
            "X-Requested-With": "XMLHttpRequest"
        }
        data = {
            "pageId": "www788",
            "movePage": str(current_page),
            "searchTy": "searchTy02",
            "searchQuery": "주유소" # 이 검색어가 totalCnt에 영향을 주는지 다시 확인
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status() # HTTP 오류 발생 시 예외 발생
            json_data = response.json()

            if json_data.get("error") == "N" and "dataMap" in json_data:
                data_map = json_data["dataMap"]
                stores_on_page = data_map.get("list", [])
                total_count = data_map.get("totalCnt", 0)

                # 첫 페이지에서만 전체 페이지 수 계산
                if current_page == 1:
                    total_pages = math.ceil(total_count / page_size)
                    print(f"API에서 총 {total_count}개의 업체 정보를 반환했습니다. {total_pages} 페이지를 수집합니다.")

                print(f"페이지 {current_page}/{total_pages} 에서 {len(stores_on_page)}개 데이터 수집 중...")

                for store in stores_on_page:
                    store_name = store.get("storeNm", "").strip()
                    address = store.get("storeAddr", "").strip()
                    store_category = store.get("storeCtgy", "").strip() # 업종명 추가

                    # 업종명(storeCtgy)을 기준으로 필터링
                    if store_category in ALLOWED_CATEGORIES:
                        all_stores.append({
                            "업체명": store_name,
                            "업체주소": address,
                            "업종명": store_category # 업종명도 저장
                        })
            else:
                print(f"API 응답 오류: {json_data.get('error')}")
                break

        except requests.exceptions.RequestException as e:
            print(f"요청 중 오류 발생: {e}")
            break
        except ValueError as e:
            print(f"JSON 파싱 오류: {e}")
            print(f"응답 내용: {response.text[:500]}...") # 응답 내용 일부 출력
            break
        
        current_page += 1
        time.sleep(0.5) # 서버 부하를 줄이기 위한 짧은 대기

    # 수집된 데이터를 DataFrame으로 변환하고 CSV로 저장
    if all_stores:
        # 중복 제거
        df = pd.DataFrame(all_stores)
        df.drop_duplicates(inplace=True)
        
        # CSV 파일로 저장
        output_filename = "gjssoil_stores.csv"
        df.to_csv(output_filename, index=False, encoding="utf-8-sig")
        print(f"\n총 {len(df)}개의 필터링된 주유소 정보를 '{output_filename}' 파일로 저장했습니다.")
    else:
        print("\n수집된 데이터가 없습니다.")

if __name__ == "__main__":
    scrape_gwangju_gas_stations()