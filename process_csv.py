import pandas as pd

def process_sangsaeng_csv():
    csv_file_path = "D:\\Vault\\gemini\\gjssoil\\광주광역시_상생카드가맹점현황_20240915.csv"
    output_filename = "gjssoil_stores.csv"

    # 필터링할 업종명 목록
    ALLOWED_CATEGORIES = [
        "E1가스충전소", "GS가스충전호", "GS주유소", "L P G", "SK가스충전소",
        "SK주유소", "쌍용S-oil가스충전소", "쌍용S-oil주유소", "주 유 소",
        "현대정유가스충전소", "현대정유오일뱅크"
    ]

    print(f"CSV 파일 '{csv_file_path}'을(를) 읽는 중...")
    try:
        # CSV 파일 읽기 (encoding='cp949' 또는 'euc-kr' 시도)
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_file_path, encoding='cp949')
            except UnicodeDecodeError:
                df = pd.read_csv(csv_file_path, encoding='euc-kr')

        print(f"총 {len(df)}개의 데이터가 로드되었습니다.")

        # '업종명' 컬럼을 기준으로 필터링
        # 컬럼명이 다를 경우를 대비하여 대소문자 구분 없이 '업종명' 또는 '업종'을 찾도록 함
        category_col = None
        for col in df.columns:
            if '업종명' in col or '업종' in col:
                category_col = col
                break
        
        if category_col:
            filtered_df = df[df[category_col].isin(ALLOWED_CATEGORIES)].copy()
            # 필요한 컬럼만 선택 (업체명, 업체주소, 업종명)
            # 실제 CSV 파일의 컬럼명에 따라 조정 필요
            # 여기서는 '업체명', '업체주소', '업종명'이 있다고 가정
            # 만약 컬럼명이 다르다면, 실제 컬럼명으로 변경해야 합니다.
            # 예: filtered_df = filtered_df[['가맹점명', '주소', '업종']].copy()
            
            # 컬럼명 통일 (업체명, 업체주소, 업종명)
            # 실제 CSV 파일의 컬럼명과 매핑 필요
            column_mapping = {
                '업체명': '업체명',
                '업체주소': '업체주소',
                category_col: '업종명' # 실제 업종명 컬럼을 '업종명'으로 매핑
            }
            # CSV 파일의 실제 컬럼명에 따라 이 부분을 조정해야 합니다.
            # 예를 들어, '가맹점명'이 실제 업체명 컬럼이라면 '가맹점명': '업체명'으로 변경
            
            # 현재 데이터프레임의 컬럼 중 매핑 가능한 컬럼만 선택
            cols_to_select = [col for col in column_mapping.keys() if col in filtered_df.columns]
            filtered_df = filtered_df[cols_to_select].rename(columns=column_mapping)

            # 중복 제거
            filtered_df.drop_duplicates(inplace=True)

            filtered_df.to_csv(output_filename, index=False, encoding="utf-8-sig")
            print(f"\n총 {len(filtered_df)}개의 필터링된 주유소 정보가 '{output_filename}' 파일로 저장되었습니다.")
        else:
            print("오류: '업종명' 또는 '업종' 컬럼을 찾을 수 없습니다. CSV 파일의 컬럼명을 확인해주세요.")

    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다. 경로를 확인해주세요: {csv_file_path}")
    except Exception as e:
        print(f"CSV 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    process_sangsaeng_csv()