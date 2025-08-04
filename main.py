import os
import time
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 설정 ---
# .env 파일에서 환경 변수 로드
load_dotenv()
MUSINSA_ID = os.getenv("MUSINSA_ID")
MUSINSA_PASSWORD = os.getenv("MUSINSA_PASSWORD")

# URL 정의
LOGIN_URL = "https://www.musinsa.com/auth/login?referer=https%3A%2F%2Fwww.musinsa.com%2Forders%2Fcart"
MY_PAGE_URL = "https://www.musinsa.com/order/order-list"

# 이미지 저장 폴더
IMAGE_SAVE_DIRECTORY = "images"

# --- 함수 정의 ---

def setup_driver():
    """Selenium WebDriver를 설정하고 반환합니다."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 백그라운드에서 실행하려면 주석 해제
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def login(driver, user_id, password):
    """무신사 웹사이트에 로그인합니다."""
    print("로그인 페이지로 이동합니다...")
    driver.get(LOGIN_URL)

    if not user_id or not password:
        print("오류: .env 파일에 MUSINSA_ID와 MUSINSA_PASSWORD를 설정해야 합니다.")
        return False

    try:
        print(f"{user_id} 계정으로 로그인을 시도합니다...")
        
        # 페이지 로딩을 위해 잠시 대기
        time.sleep(3)
        
        # 다양한 선택자로 아이디 입력 필드 찾기
        id_input = None
        id_selectors = [
            "input[name='id']",
            "input[name='userId']", 
            "input[name='loginId']",
            "input[name='username']",
            "input[type='text']",
            "#id",
            "#userId", 
            "#loginId",
            "#username"
        ]
        
        for selector in id_selectors:
            try:
                id_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"아이디 입력 필드를 찾았습니다: {selector}")
                break
            except:
                continue
                
        if not id_input:
            print("아이디 입력 필드를 찾을 수 없습니다. 페이지 구조를 확인하세요.")
            return False

        # 다양한 선택자로 비밀번호 입력 필드 찾기
        pw_input = None
        pw_selectors = [
            "input[name='pw']",
            "input[name='password']",
            "input[name='passwd']",
            "input[type='password']",
            "#pw",
            "#password",
            "#passwd"
        ]
        
        for selector in pw_selectors:
            try:
                pw_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"비밀번호 입력 필드를 찾았습니다: {selector}")
                break
            except:
                continue
                
        if not pw_input:
            print("비밀번호 입력 필드를 찾을 수 없습니다. 페이지 구조를 확인하세요.")
            return False

        # 아이디와 비밀번호 입력
        id_input.clear()
        id_input.send_keys(user_id)
        time.sleep(1)
        pw_input.clear()
        pw_input.send_keys(password)
        time.sleep(1)

        # 다양한 선택자로 로그인 버튼 찾기
        login_button = None
        login_selectors = [
            ".login-button.btn.btn-primary",
            "button[type='submit']",
            "input[type='submit']",
            ".btn-login",
            ".login-btn",
            "#loginBtn",
            "#login-button",
            "button:contains('로그인')",
            "input[value*='로그인']"
        ]
        
        for selector in login_selectors:
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"로그인 버튼을 찾았습니다: {selector}")
                break
            except:
                continue
                
        if not login_button:
            print("로그인 버튼을 찾을 수 없습니다. Enter 키로 로그인을 시도합니다.")
            pw_input.send_keys(Keys.ENTER)
        else:
            login_button.click()

        # 로그인 성공 확인 (마이페이지로 리디렉션 될 때까지 대기)
        WebDriverWait(driver, 20).until(
            EC.url_contains("https://www.musinsa.com")
        )
        print("로그인 성공!")
        return True
    except Exception as e:
        print(f"로그인 중 오류가 발생했습니다: {e}")
        print("CAPTCHA 또는 다른 로그인 문제가 발생했을 수 있습니다. 브라우저를 확인하세요.")
        time.sleep(30) # 수동으로 해결할 시간
        return False

def crawl_images(driver):
    """구매 내역 페이지에서 상품 이미지를 크롤링합니다."""
    print("구매 내역 페이지로 이동합니다...")
    driver.get(MY_PAGE_URL)

    # 이미지 저장 디렉토리 생성
    if not os.path.exists(IMAGE_SAVE_DIRECTORY):
        os.makedirs(IMAGE_SAVE_DIRECTORY)

    print("이미지 크롤링을 시작합니다...")
    try:
        # 페이지 끝까지 스크롤하여 모든 상품 로드
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 새 콘텐츠가 로드될 시간
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # 상품 이미지 요소 찾기
        image_elements = driver.find_elements(By.CSS_SELECTOR, ".box_list_area .list_img > a > img")
        if not image_elements:
            print("구매 내역에서 상품 이미지를 찾을 수 없습니다.")
            return

        print(f"총 {len(image_elements)}개의 상품 이미지를 찾았습니다.")

        # 이미지 다운로드
        for index, img in enumerate(image_elements):
            try:
                # 'lazyload' 클래스를 가진 경우 'data-original' 속성 사용
                if 'lazyload' in img.get_attribute('class'):
                    image_url = img.get_attribute('data-original')
                else:
                    image_url = img.get_attribute('src')

                if not image_url.startswith('http'):
                    image_url = "https:" + image_url

                # 이미지 다운로드 및 저장
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    # 파일 이름 생성 (예: 001.jpg)
                    filename = f"{str(index + 1).zfill(3)}.jpg"
                    filepath = os.path.join(IMAGE_SAVE_DIRECTORY, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"({index + 1}/{len(image_elements)}) {filename} 저장 완료")
                else:
                    print(f"이미지 다운로드 실패: {image_url} (상태 코드: {response.status_code})")

            except Exception as e:
                print(f"이미지 처리 중 오류 발생: {e}")

        print("모든 이미지 다운로드가 완료되었습니다.")

    except Exception as e:
        print(f"이미지 크롤링 중 오류가 발생했습니다: {e}")


# --- 메인 실행 ---
if __name__ == "__main__":
    driver = setup_driver()
    try:
        if login(driver, MUSINSA_ID, MUSINSA_PASSWORD):
            crawl_images(driver)
    finally:
        print("5초 후에 브라우저를 종료합니다.")
        time.sleep(5)
        driver.quit()
        print("프로그램을 종료합니다.")
