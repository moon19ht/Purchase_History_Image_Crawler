# 무신사 구매 내역 이미지 크롤러

이 프로젝트는 [Selenium](https://www.selenium.dev/)을 사용하여 무신사(Musinsa) 웹사이트에 자동으로 로그인하고, 사용자의 전체 구매 내역에 있는 상품 이미지들을 크롤링하여 로컬 폴더에 저장하는 자동화 스크립트입니다.

## ✨ 주요 기능

-   **자동 로그인**: 무신사 계정으로 안전하게 자동 로그인합니다.
-   **구매 내역 접근**: 로그인 후 마이페이지의 구매 내역 페이지로 이동합니다.
-   **이미지 크롤링**: 전체 구매 내역을 탐색하며 모든 상품의 썸네일 이미지를 추출합니다.
-   **이미지 저장**: 크롤링한 이미지를 지정된 로컬 폴더(`images`)에 저장합니다.

## 🛠️ 기술 스택 및 요구사항

-   Python 3.8 이상
-   [Selenium](https://www.selenium.dev/): 웹 브라우저 자동화 라이브러리
-   [webdriver-manager](https://pypi.org/project/webdriver-manager/): 웹 드라이버 자동 관리를 위한 라이브러리

## ⚙️ 설치 및 설정 방법

### 1. 프로젝트 클론

```bash
git clone https://github.com/your-username/musinsa-crawler.git
cd musinsa-crawler
```

### 2. 가상 환경 생성 및 활성화

프로젝트의 의존성을 독립적으로 관리하기 위해 가상 환경을 사용하는 것을 권장합니다.

-   **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
-   **macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3. 의존성 설치

프로젝트에 필요한 라이브러리들을 설치합니다.

```bash
pip install -r requirements.txt
```

> **참고**: `requirements.txt` 파일이 없다면 아래 명령어로 직접 라이브러리를 설치하세요.
>
> ```bash
> pip install selenium webdriver-manager python-dotenv
> ```

### 4. 환경 변수 설정

보안을 위해 아이디와 비밀번호를 코드에 직접 하드코딩하지 않고, `.env` 파일을 통해 관리합니다.

-   프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래와 같이 내용을 작성하세요.

    ```env
    # .env 파일
    MUSINSA_ID="여기에_무신사_아이디를_입력하세요"
    MUSINSA_PASSWORD="여기에_무신사_비밀번호를_입력하세요"
    ```

-   `.gitignore` 파일에 `.env` 파일이 포함되어 있는지 확인하여 민감한 정보가 Git에 커밋되지 않도록 하세요.

    ```gitignore
    # .gitignore
    .env
    venv/
    __pycache__/
    *.pyc
    images/
    ```

## ▶️ 실행 방법

모든 설정이 완료되었다면, 아래 명령어를 통해 크롤러를 실행할 수 있습니다.

```bash
python main.py
```

스크립트가 실행되면 다음 과정이 자동으로 진행됩니다.

1.  Chrome 브라우저가 열립니다.
2.  무신사 로그인 페이지로 이동하여 `.env` 파일에 입력된 정보로 로그인합니다.
3.  마이페이지의 구매 내역으로 이동합니다.
4.  구매한 모든 상품의 이미지를 크롤링하여 프로젝트 내 `images` 폴더에 저장합니다.

## ⚠️ 주의사항

-   본 스크립트는 개인적인 학습 및 사용 목적으로 제작되었습니다.
-   웹사이트의 구조가 변경될 경우 스크립트가 정상적으로 동작하지 않을 수 있습니다.
-   과도한 크롤링 요청은 웹사이트에 부하를 줄 수 있으며, 계정이 차단될 위험이 있습니다. 책임감 있게 사용해 주세요.
-   이 스크립트의 사용으로 인해 발생하는 모든 문제에 대한 책임은 전적으로 사용자 본인에게 있습니다.
