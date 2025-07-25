# gjssoil 프로젝트 구현 및 문제 해결 요약

이 문서는 "광주 상생카드 가맹 주유소 가격 정보" 웹페이지를 구현하고, 그 과정에서 발생한 주요 문제점들을 해결한 내역을 단계별로 상세히 기술합니다.

## 1. 프로젝트 초기 설정 및 워크플로우 정의

프로젝트의 목표는 광주 상생카드 가맹 주유소의 가격 정보를 수집하여 웹페이지에 표시하는 것이었습니다. 초기 워크플로우는 다음과 같았습니다.

*   **원본 데이터 소스:**
    *   `광주광역시_상생카드가맹점현황_20240915.csv` (상생카드 가맹점 목록)
    *   `광주전체주유소충전소.csv` (오피넷 광주 주유소/충전소 목록)
*   **데이터 처리 단계 (Python 스크립트):**
    1.  `matching_stn_info.py`: 상생카드 데이터에서 주유소/충전소를 추출하고 오피넷 데이터와 매칭하여 `gjssoil_list.csv` 생성.
    2.  `get_more_stn_info.py`: `gjssoil_list.csv`를 바탕으로 오피넷 API를 호출하여 상세 정보(`gjssoil_info.csv`) 획득.
    3.  `generate_gjssoil_data.py`: `gjssoil_info.csv`의 `UNI_ID`로 오피넷 API에서 유가 정보를 가져와 최종 JSON/CSV 데이터(`gjssoil_data.json`, `gjssoil_data.csv`) 생성.
*   **웹페이지 게시 단계:** GitHub Actions를 통해 `index.html`과 생성된 데이터를 GitHub Pages에 배포.

## 2. 사용자 데이터 수정 단계 도입 및 `matching_stn_info.py` 개선

사용자 요청에 따라, 1단계와 2단계 사이에 수동 데이터 수정 단계가 추가되었습니다.

*   **수동 수정:** 엑셀 필터를 사용하여 상생카드 가맹점 데이터에서 주유소/충전소만 남기고, 오피넷 자료와 비교하여 업체명과 주소를 일치시켰습니다. 업체명이 다른 경우 오피넷 자료를 기준으로 상생카드 가맹점 자료의 업체명을 수정하여 `gjssoil_stores_mod.csv` 파일을 생성했습니다.
*   **`matching_stn_info.py` 수정:** `matching_stn_info.py`는 이제 `광주광역시_상생카드가맹점현황_20240915.csv` 대신 `gjssoil_stores_mod.csv`를 주 입력으로 사용하여 오피넷 데이터와 매칭하도록 변경되었습니다. 이 과정에서 93개 업체 중 91개(이후 92개)만 최종 목록에 포함되는 현상이 발생했으며, 이는 오피넷 데이터와의 정확한 상호명 일치 여부에 따른 결과였습니다.

## 3. 웹페이지 초기 표시 문제 및 디버깅

웹페이지 배포 후, 목록과 지도가 제대로 표시되지 않는 문제가 발생했습니다.

*   **문제 원인:** `index.html`의 JavaScript 코드가 `gjssoil_data.json` 파일을 사용하지 않고, `gjssoil_stores.csv`를 직접 읽어와 클라이언트 측에서 오피넷 API를 호출하도록 설계되어 있었습니다. 이는 백엔드 스크립트(`generate_gjssoil_data.py`)의 작업 결과가 웹페이지에 반영되지 않는 원인이었습니다.
*   **해결 시도:**
    *   `index.html`을 수정하여 `gjssoil_data.json`을 직접 로드하도록 변경했습니다.
    *   초기에는 `gjssoil_data.json`의 필드명(`OS_NM`, `NEW_ADR` 등)과 JavaScript 코드에서 사용하는 변수명(`name`, `address` 등)의 불일치로 인해 "undefined" 오류가 발생했습니다.
    *   `index.html`의 JavaScript 코드를 다시 수정하여 `gjssoil_data.json`의 실제 필드명을 올바르게 참조하도록 변경했습니다.

## 4. 좌표계 변환 문제 해결 (거리 계산 오류)

웹페이지에 주유소 정보는 표시되었으나, 거리 계산 결과가 비정상적으로 크게 나오는 문제(수천 km)가 발생했습니다.

*   **문제 원인:** 오피넷 API에서 제공하는 `GIS_X_COOR`, `GIS_Y_COOR` 좌표가 WGS84 위도/경도가 아닌 TM 좌표계(Transverse Mercator)였으며, `generate_gjssoil_data.py`에서 이 TM 좌표를 WGS84로 변환하는 과정에 오류가 있었습니다.
*   **해결 과정 (시행착오):**
    *   **가설 1 (EPSG:5186):** `pyproj`를 사용하여 KATEC (EPSG:5186)에서 WGS84로 변환을 시도했으나, 여전히 오차가 발생했습니다.
    *   **가설 2 (EPSG:5179):** 다른 KATEC 버전인 EPSG:5179를 시도했으나, 역시 오차가 있었습니다.
    *   **가설 3 (EPSG:5174):** EPSG:5174를 시도했으나, 위도 오차까지 발생했습니다.
    *   **결정적 단서 (TM128 및 `towgs84`):** 사용자께서 "TM128" 좌표계 정보를 제공해주셨고, 관련 블로그에서 `proj4` 문자열을 얻었습니다. 이 `proj4` 문자열에는 `+towgs84`라는 변환 파라미터가 포함되어 있었습니다.
    *   **최종 해결:** `generate_gjssoil_data.py`에서 `pyproj.Transformer`를 초기화할 때, **`+towgs84` 파라미터를 제외한 TM128 `proj4` 문자열을 사용하여 변환**하도록 수정했습니다. `towgs84` 파라미터가 잘못되었을 경우 오히려 변환 오차를 유발할 수 있었던 것입니다. 이 수정으로 `gjssoil_data.json`에 저장되는 `LAT`, `LNG` 값이 광주광역시의 실제 위도/경도 범위와 일치하게 되었고, 거리 계산도 정상화되었습니다.
*   **디버깅 방법:** `generate_gjssoil_data.py`에 `print` 문을 추가하여 변환된 `LAT`, `LNG` 값을 GitHub Actions 로그에서 직접 확인하며 좌표계 변환의 정확성을 검증했습니다.

## 5. 웹페이지 UI/UX 개선 및 자동화

*   **"현위치" 버튼 추가:** 브라우저의 위치 정보 요청 보안 정책을 고려하여, 사용자가 명시적으로 위치 정보를 요청할 수 있는 "현위치" 버튼을 추가했습니다.
*   **지도 기능 제거:** API 키 노출 문제와 웹페이지의 복잡성을 줄이기 위해 사용자 요청에 따라 지도 기능을 완전히 제거했습니다. 이로써 카카오맵 API 키에 대한 의존성이 사라졌습니다.
*   **문구 수정:**
    *   "광주 상생카드 가맹 주유소 최저가 찾기" -> "광주 상생카드 가맹 주유소 가격 정보"
    *   "본 데이터는 공공데이터포털과 오피넷 API를 기반으로 제공됩니다." -> "본 데이터는 공공데이터포털과 오피넷 API를 기반으로 제공하고 있으나, 누락된 정보가 있을 수 있으니 주의가 필요합니다."
*   **GitHub Actions 자동화:** `gjssoil/.github/workflows/deploy.yml` 파일에 `schedule` 트리거를 추가하여 매일 세 번(오전 8시, 오후 1시, 오후 6시 KST) 자동으로 데이터 수집 및 웹페이지 배포가 이루어지도록 설정했습니다.
*   **GitHub Actions 경로 문제 해결:** `deploy.yml`에서 Python 스크립트 실행 시 `gjssoil/` 경로가 중복되어 발생했던 "No such file or directory" 오류를 수정했습니다.

## 6. 결론

이 프로젝트는 데이터 처리, 좌표계 변환, 웹페이지 구현 및 자동화에 이르는 다양한 소프트웨어 엔지니어링 과제를 포함했습니다. 특히 좌표계 변환 문제는 정확한 `proj4` 정의를 찾는 것이 중요하며, `towgs84`와 같은 변환 파라미터의 영향력을 이해하는 것이 핵심이었습니다. 지속적인 디버깅과 사용자 피드백을 통해 문제를 해결하고 기능을 개선할 수 있었습니다.

## 7. 웹페이지 기능 개선 및 오류 수정

웹페이지의 사용자 경험을 개선하고 발생한 오류를 해결했습니다.

*   **거리-가격 산점도 기능 추가:**
    *   '거리-가격 산점도' 토글 버튼을 추가하여 주유소 목록과 산점도 뷰를 전환할 수 있도록 구현했습니다.
    *   산점도에서 주유소의 거리와 가격을 시각적으로 확인할 수 있으며, 평균 거리 및 평균 가격을 나타내는 선을 추가했습니다.
    *   산점도 차트의 크기를 정사각형으로 고정하여 가독성을 높였습니다.
    *   산점도 상의 점을 클릭하면 해당 주유소의 상세 정보가 차트 하단에 표시되도록 했습니다.
*   **데이터 필드명 불일치 수정:**
    *   `gjssoil_data.json` 파일의 필드명(`OS_NM`, `NEW_ADR`)과 JavaScript 코드에서 사용하는 필드명(`name`, `address`)의 불일치로 인해 주유소 목록 및 산점도 툴팁에 정보가 올바르게 표시되지 않던 문제를 해결했습니다.
    *   JavaScript 코드 내에서 `store.name`을 `store.OS_NM`으로, `store.address`를 `store.NEW_ADR`로 수정하여 데이터가 올바르게 매핑되도록 했습니다.
*   **`gjssoil_data.json` 로딩 경로 수정:**
    *   로컬 환경에서 `gjssoil_data.json` 파일 로딩 실패 문제가 발생하여, `fetchJsonData` 함수에서 `jsonUrl`을 현재 페이지의 절대 경로를 기준으로 구성하도록 수정했습니다.
*   **GitHub Actions 워크플로우 최적화:**
    *   `matching_stn_info.py`와 `get_more_stn_info.py` 스크립트가 현재 워크플로우에서 불필요하다고 판단되어 `deploy.yml`에서 해당 스텝을 제거했습니다.
    *   Python 스크립트에서 오피넷 API 키를 환경 변수(`OPINET_API_KEY`)에서 가져오도록 수정하고, GitHub Actions 워크플로우에서 해당 환경 변수를 스크립트에 전달하도록 `deploy.yml` 파일을 업데이트했습니다.
    *   `get_more_stn_info.py` 파일 내의 Windows 절대 경로를 상대 경로로 수정하여 `SyntaxWarning`을 해결했습니다.
