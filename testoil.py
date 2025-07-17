import pandas as pd
from rapidfuzz import fuzz

# 파일 불러오기
a = pd.read_csv('D:/Vault/gemini/gjssoil/gjssoil_stores.csv')
b = pd.read_csv('D:/Vault/gemini/gjssoil/광주전체주유소충전소.csv')

# 결측치 제거
a = a.dropna(subset=['업체주소', '업체명'])
b = b.dropna(subset=['주소', '상호'])

# 주소와 업체명 리스트 생성
addresses_a = a['업체주소'].tolist()
names_a = a['업체명'].tolist()

# 주소 기반 유사도 필터링
filtered_rows = []
for idx_b, row_b in b.iterrows():
    address_b = row_b['주소']
    name_b = row_b['상호']
    matched = False

    for addr_a, name_a in zip(addresses_a, names_a):
        if fuzz.ratio(addr_a, address_b) >= 80:
            # 주소가 유사한 경우, 업체명도 비교
            if fuzz.ratio(name_a, name_b) >= 85:
                matched = True
                break

    if matched:
        filtered_rows.append(row_b)

# 결과 DataFrame 생성
filtered_df = pd.DataFrame(filtered_rows)

# 저장
filtered_df.to_csv('D:/Vault/gemini/gjssoil/filtered_b.csv', index=False)

# 미리 보기
print(filtered_df[['상호', '주소']].head())
