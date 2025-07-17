# gjssoil 프로젝트 추진 계획

## 1. 프로젝트 개요

*   **프로젝트명:** gjssoil
*   **목표:** 광주 상생카드 가맹 주유소 및 LPG 충전소의 실시간(또는 준실시간) 유가 정보를 목록과 지도로 제공하는 웹 서비스 개발.
*   **핵심 기능:**
    *   광주 상생카드 가맹 주유소 목록 표시
    *   오피넷 API를 통한 유가 정보 연동
    *   카카오 지도 API를 통한 지도 기반 정보 제공
    *   목록/지도 뷰 전환, 거리/가격순 정렬
*   **기술 스택:** HTML, CSS (Tailwind CSS), JavaScript, Python (데이터 처리), Kakao Maps API, Opinet API, GitHub Pages, GitHub Actions.

## 2. 현재까지의 진행 상황 (2025년 7월 9일 기준)

### 2.1. 프론트엔드 기본 구조 구축
*   `index.html` 파일에 웹 서비스의 기본 UI (헤더, 컨트롤, 목록 영역, 지도 영역, 푸터)가 구현되었습니다.
*   Tailwind CSS를 사용하여 기본적인 스타일링이 적용되었습니다.
*   목록/지도 뷰 전환, 정렬 기능의 UI 요소가 준비되었습니다.

### 2.2. 상생카드 가맹점 데이터 확보 전략 변경
*   **기존:** 공공데이터포털 API를 통해 실시간으로 가맹점 정보를 가져오는 방식.
*   **변경:** 공공데이터포털 API의 업데이트 주기가 길다는 점을 고려하여, 미리 다운로드된 CSV 파일(`광주광역시_상생카드가맹점현황_20240915.csv`)을 사용하는 방식으로 변경되었습니다.
*   **구현:** `process_csv.py` 스크립트가 개발되어 원본 CSV 파일에서 주유소/충전소 업종만 필터링하여 `gjssoil_stores.csv` 파일을 생성합니다. (총 127개 업체 확인)

### 2.3. 오피넷 유가 정보 연동 전략 변경 및 문제점 파악
*   **기존:** 프론트엔드(`index.html`)에서 직접 오피넷 API를 호출하여 실시간 유가 정보를 가져오는 방식.
*   **변경:** 유가 정보가 실시간으로 반영될 필요는 없으며, 하루 3회 업데이트하는 방식으로 변경되었습니다. 이를 위해 백엔드에서 데이터를 미리 처리하는 방식으로 전환되었습니다.
*   **구현:** `generate_gjssoil_data.py` 스크립트가 개발되어 `gjssoil_stores.csv`의 업체명으로 오피넷 API를 호출하여 가격 정보를 가져오고, 이를 `gjssoil_data.json` 및 `gjssoil_data.csv` 파일로 저장합니다.
*   **문제점 파악:** `generate_gjssoil_data.py` 실행 결과, 오피넷 API의 `searchByName.do` 엔드포인트가 업체명으로 검색 시 전국 단위의 동일 상호 주유소를 모두 반환하여, 광주 지역 주유소의 정확한 가격 정보를 매칭하기 어렵다는 문제가 확인되었습니다. 이로 인해 `gjssoil_data.json`의 가격 정보가 비어있는 경우가 발생했습니다.

### 2.4. 오피넷 유가 정보 연동 개선을 위한 새로운 전략 수립
*   **문제 해결 방안:** 오피넷 API의 `areaSearch.do` 엔드포인트를 사용하여 광주광역시 내의 모든 주유소 목록과 고유 ID(`UNI_ID`)를 먼저 확보하는 전략을 수립했습니다. `UNI_ID`를 알면 `detailSearch.do` 엔드포인트를 통해 해당 주유소의 정확한 가격 정보를 가져올 수 있습니다.
*   **구현:** `get_gwangju_opinet_stations.py` 스크립트가 개발되어 오피넷 API `areaSearch.do`를 통해 광주광역시의 주유소 목록과 `UNI_ID`를 `opinet_gwangju_stations.csv` 파일로 저장하는 기능을 가집니다.

### 2.5. API 키 관리 및 배포
*   **API 키 관리:** GitHub Secrets를 사용하여 API 키를 안전하게 관리하고, GitHub Actions 워크플로우에서 `sed` 명령어를 통해 `index.html`의 플레이스홀더를 실제 키로 치환하는 방식을 사용합니다.
*   **배포:** GitHub Pages를 통해 웹 서비스가 배포됩니다.
*   **현재 문제:** `index.html`의 `KAKAO_API_KEY` 플레이스홀더가 GitHub Actions에서 제대로 치환되지 않는 문제가 있었으며, `gjssoil_data.json` 파일이 GitHub Pages에 배포되지 않아 웹페이지에서 데이터를 불러오지 못하는 문제가 있습니다.

## 3. 향후 추진 계획 (남은 작업)

### 3.1. 오피넷 데이터 연동 로직 최종 개선
1.  **`get_gwangju_opinet_stations.py` 실행 및 `UNI_ID` 확보:**
    *   `get_gwangju_opinet_stations.py` 스크립트를 실행하여 `opinet_gwangju_stations.csv` 파일을 생성합니다. (오피넷 API 키 입력 필요)
2.  **`generate_gjssoil_data.py` 수정 및 실행:**
    *   `generate_gjssoil_data.py` 스크립트를 수정하여:
        *   `gjssoil_stores.csv` (상생카드 가맹점 목록)를 로드합니다.
        *   `opinet_gwangju_stations.csv` (오피넷 광주 주유소 목록 + `UNI_ID`)를 로드합니다.
        *   **매칭** 상생카드 가맹점과 오피넷 주유소를 업체명과 주소(또는 주소의 일부)를 기반으로 매칭하여, 상생카드 가맹점의 정확한 `UNI_ID`를 찾아냅니다.
        *   매칭된 `UNI_ID`를 사용하여 오피넷 API의 `detailSearch.do` (또는 `areaSearch.do`가 가격 정보를 제공한다면) 엔드포인트를 호출하여 정확한 유가 정보를 가져옵니다.
        *   가져온 유가 정보를 포함하여 `gjssoil_data.json` 및 `gjssoil_data.csv` 파일을 생성합니다.
    *   수정된 스크립트를 실행하여 최신 데이터 파일을 생성합니다.

### 3.2. 프론트엔드 최종 통합 및 검증
1.  **`index.html` 데이터 로딩 검증:** `index.html`이 새로 생성된 `gjssoil_data.json` 파일을 올바르게 불러오고 파싱하는지 확인합니다.
2.  **UI 표시 검증:** 주유소 목록과 지도 마커, 팝업 정보(업체명, 주소, 휘발유/경유/LPG 가격)가 올바르게 표시되는지 확인합니다.
3.  **카카오 지도 API 키 치환 확인:** `index.html`의 `KAKAO_API_KEY` 플레이스홀더가 GitHub Actions에서 올바르게 치환되는지 최종 확인합니다. (필요시 `deploy.yml`의 `sed` 명령어 재검토)

### 3.3. 배포 및 최종 확인
1.  **Git 변경사항 커밋 및 푸시:**
    *   `gjssoil_data.json`, `gjssoil_data.csv` 파일을 포함하여 모든 변경된 파일들을 Git에 추가하고 커밋합니다.
    *   GitHub 저장소에 푸시합니다.
2.  **GitHub Pages 배포 확인:** GitHub Actions 워크플로우가 성공적으로 실행되어 GitHub Pages에 최신 버전의 웹 서비스가 배포되었는지 확인합니다.
3.  **라이브 서비스 테스트:** 배포된 웹페이지(`https://kurette683.github.io/gjssoil/`)에 접속하여 모든 기능이 정상적으로 작동하는지 최종 확인합니다.

### 3.4. 자동화 (선택 사항)
1.  **GitHub Actions 스케줄링:** `generate_gjssoil_data.py` 스크립트를 GitHub Actions의 스케줄링 기능을 사용하여 하루 3회 자동으로 실행되도록 설정합니다. 이를 통해 `gjssoil_data.json` 파일이 주기적으로 업데이트되도록 합니다.

---
