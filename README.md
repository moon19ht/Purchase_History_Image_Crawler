# 무신사 구매내역 이미지 크롤러

무신사(Musinsa) 구매 내역에서 상품 이미지를 자동으로 다운로드하는 Python 웹 스크래핑 도구입니다.

## ✨ 주요 기능

- **자동 로그인**: 무신사 계정 자동 로그인 및 세션 관리
- **전체 구매내역 탐색**: 페이지네이션을 통한 모든 구매 내역 로드
- **고품질 이미지 다운로드**: 썸네일을 고해상도 버전으로 자동 변환
- **중복 제거 및 품질 필터링**: 동일 이미지 제거 및 저품질 이미지 필터링
- **이미지 후처리**: 브랜드별 정리, 형식 변환, 크기 조정
- **진행률 추적**: 실시간 다운로드 진행률 및 상세 로그

## 🚀 빠른 시작

### 1. 필수 요구사항
- **Python 3.7 이상**
- **Firefox 브라우저** (권장) 또는 Chrome
- 안정적인 인터넷 연결
- 무신사 계정 (구매 내역이 있어야 함)

### 2. 설치
```bash
# 저장소 클론
git clone https://github.com/your-username/Purchase_History_Image_Crawler.git
cd Purchase_History_Image_Crawler

# 의존성 설치 (uv 권장)
uv pip install -r requirements.txt

# 또는 pip 사용
pip install -r requirements.txt
```

### 3. 실행
```bash
# Firefox 기반 크롤러 (권장)
python crawler_main_firefox.py

# 이미지 관리 도구
python utils.py <다운로드된_폴더_경로>
```

## ⚙️ 설정 옵션

처음 실행하면 `crawler_config.json` 파일이 생성됩니다:

```json
{
  "max_images": 1000,           // 최대 다운로드 이미지 수
  "download_delay": 0.5,        // 다운로드 간 지연 시간(초)
  "page_load_timeout": 30,      // 페이지 로드 타임아웃(초)
  "implicit_wait": 10,          // 요소 대기 시간(초)
  "retry_attempts": 3,          // 로그인 재시도 횟수
  "image_quality_filter": true, // 저품질 이미지 필터링
  "headless_mode": false        // 브라우저 창 숨김 여부
}
```

## 📁 프로젝트 구조

```
Purchase_History_Image_Crawler/
├── crawler_main_firefox.py    # 메인 크롤러 (Firefox 기반)
├── utils.py                   # 이미지 분석 및 관리 도구
├── crawler_config.json        # 설정 파일 (자동 생성)
├── requirements.txt           # Python 의존성
├── README.md                  # 사용 가이드
├── CLAUDE.md                  # AI 개발 도우미 가이드
└── .gitignore                 # Git 무시 파일
```

## 📁 출력 구조

크롤링 완료 후 다음과 같은 구조로 파일이 저장됩니다:

```
musinsa_images_20240805_143022/
├── musinsa_brand_productid_001.jpg
├── musinsa_brand_productid_002.webp
├── ...
├── download_info.json          # 다운로드 상세 정보
└── session_log.json           # 세션 로그
```

## 🔧 고급 기능

### 1. 고해상도 이미지 변환
스크립트는 자동으로 썸네일을 고해상도 버전으로 변환하려고 시도합니다:
- `thumb` → `large`
- `small` → `origin`
- `150px` → `500px`

### 2. 품질 필터링
5KB 미만의 작은 이미지나 아이콘은 자동으로 제외됩니다.

### 3. 중복 제거
동일한 이미지 URL은 자동으로 중복 제거됩니다.

### 4. 진행률 표시
다운로드 진행 상황을 실시간으로 확인할 수 있습니다.

## 🔍 문제 해결

### Firefox 관련 오류
**오류**: `GeckoDriver` 관련 오류
**해결**: 
- Firefox 브라우저가 설치되어 있는지 확인
- `webdriver-manager`가 자동으로 GeckoDriver를 다운로드
- Firefox 업데이트 후 재시도

### 로그인 실패
**오류**: 로그인이 계속 실패
**해결**:
1. 아이디/비밀번호 재확인
2. 무신사 웹사이트에서 직접 로그인 테스트
3. 2FA(2단계 인증) 비활성화 확인
4. `retry_attempts` 설정 증가

### 이미지가 다운로드되지 않음
**오류**: 이미지 URL을 찾을 수 없음
**해결**:
1. 구매 내역이 실제로 존재하는지 확인
2. 네트워크 연결 상태 확인
3. `headless_mode`를 `false`로 설정하여 브라우저 창 확인

### 메모리 부족
**오류**: 메모리 부족으로 중단
**해결**:
1. `max_images` 설정을 줄임 (예: 500)
2. `download_delay` 증가
3. 다른 프로그램 종료

## 📊 성능 최적화

### 빠른 다운로드
```json
{
  "download_delay": 0.1,
  "headless_mode": true,
  "image_quality_filter": false
}
```

### 안전한 다운로드 (서버 부하 최소화)
```json
{
  "download_delay": 1.0,
  "headless_mode": false,
  "retry_attempts": 5
}
```

### 고품질만 다운로드
```json
{
  "image_quality_filter": true,
  "max_images": 200
}
```

## 🚨 주의사항

1. **서버 부하**: 너무 빠른 요청은 IP 차단을 일으킬 수 있습니다
2. **저작권**: 다운로드한 이미지는 개인적 용도로만 사용하세요
3. **계정 보안**: 로그인 정보를 안전하게 보관하세요
4. **리소스 사용**: 대량 다운로드 시 네트워크와 저장공간을 고려하세요

## 🆘 지원

### 일반적인 오류 메시지와 해결방법

| 오류 메시지 | 원인 | 해결방법 |
|------------|------|----------|
| `ChromeDriver not found` | ChromeDriver 없음 | `webdriver-manager` 재설치 |
| `Login failed` | 로그인 실패 | 계정 정보 확인 |
| `No images found` | 이미지 없음 | 구매 내역 확인 |
| `Connection timeout` | 네트워크 문제 | 인터넷 연결 확인 |

### 로그 파일 확인
문제 발생 시 `session_log.json` 파일을 확인하여 상세한 오류 정보를 볼 수 있습니다.

## 🔄 업데이트 및 유지보수

무신사 웹사이트 구조가 변경되면 스크립트 업데이트가 필요할 수 있습니다. 주요 변경사항:

1. **CSS 셀렉터 업데이트**: 무신사가 클래스명이나 ID를 변경하는 경우
2. **로그인 프로세스 변경**: 2FA 도입이나 보안 강화
3. **이미지 URL 패턴 변경**: CDN 구조 변경

정기적으로 스크립트를 테스트하고 필요시 업데이트하는 것을 권장합니다.

## 🛠️ 개발 및 기여

### 개발 환경 설정
```bash
# 개발용 의존성 설치
uv pip install -r requirements.txt

# 코드 품질 도구 (선택사항)
pip install black flake8 mypy
```

### 주요 클래스 및 함수
- `AdvancedMusinsaCrawlerFirefox`: 메인 크롤러 클래스
- `ImageAnalyzer`: 이미지 분석 및 중복 제거
- `ImageOrganizer`: 브랜드/날짜별 폴더 정리
- `ImageConverter`: 형식 변환 및 크기 조정

### 기여 가이드라인
1. Fork 저장소
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 개인적 용도로만 사용하시기 바랍니다. 무신사의 이용약관을 준수하며, 서버에 과도한 부하를 주지 않도록 주의하세요.

## 🙏 감사의 말

- [Selenium](https://selenium-python.readthedocs.io/) - 웹 자동화 프레임워크
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) - WebDriver 자동 관리
- [Pillow](https://pillow.readthedocs.io/) - 이미지 처리 라이브러리