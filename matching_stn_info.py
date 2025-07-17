import pandas as pd

# 수동으로 수정한 주유소/충전소 목록 파일 경로
mod_stores_path = 'gjssoil_stores_mod.csv'
# 오피넷 원본 데이터 파일 경로
opinet_data_path = '광주전체주유소충전소.csv'
# 결과 파일 경로
output_path = 'gjssoil_list.csv'

try:
    # 1. 수동 수정한 파일 로드하여 유효한 업체명 리스트 생성
    try:
        mod_df = pd.read_csv(mod_stores_path, encoding='utf-8')
    except UnicodeDecodeError:
        mod_df = pd.read_csv(mod_stores_path, encoding='euc-kr')
    valid_station_names = mod_df['업체명'].tolist()

    # 2. 오피넷 원본 데이터 로드
    try:
        opinet_df = pd.read_csv(opinet_data_path, encoding='utf-8')
    except UnicodeDecodeError:
        opinet_df = pd.read_csv(opinet_data_path, encoding='euc-kr')

    # 3. 유효한 업체명 리스트를 기준으로 오피넷 데이터 필터링
    filtered_opinet_df = opinet_df[opinet_df['상호'].isin(valid_station_names)].copy()

    # 4. 필터링된 데이터에서 '상호' 컬럼만 추출
    final_station_list = filtered_opinet_df['상호']

    # 5. 최종 목록을 gjssoil_list.csv 파일로 저장
    final_station_list.to_csv(output_path, index=False, header=['OS_NM'], encoding='utf-8-sig')

    print(f"'{output_path}' 파일이 생성되었습니다.")
    print(f"오피넷 데이터와 수동 수정 목록을 비교하여 총 {len(final_station_list)}개의 주유소 정보를 필터링했습니다.")
    print("이 목록은 오피넷 원본 데이터에 존재하는 주유소들입니다.")

except FileNotFoundError as e:
    print(f"오류: 파일을 찾을 수 없습니다 - {e.filename}")
except Exception as e:
    print(f"스크립트 실행 중 오류가 발생했습니다: {e}")
