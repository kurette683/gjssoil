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
        # API 응답 구조에 맞게 OIL 리스트의 첫 번째 항목에 접근
        oil_list = data.get("RESULT", {}).get("OIL")
        
        if not oil_list:
            print(f"경고: UNI_ID '{uni_id}'에 대한 OIL 정보가 없습니다. 응답: {data}")
            return {}

        oil_prices_list = oil_list[0].get("OIL_PRICE")

        if oil_prices_list: # OIL_PRICE 리스트가 비어있지 않은지 확인
            for oil in oil_prices_list:
                prod_cd = oil.get("PRODCD")
                price = oil.get("PRICE")
                
                if prod_cd and price is not None:
                    # PRODCD를 키로 사용하여 모든 가격 정보를 딕셔너리에 저장
                    prices[prod_cd] = price
            
            # 모든 유종을 순회한 후 prices 딕셔너리 반환
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