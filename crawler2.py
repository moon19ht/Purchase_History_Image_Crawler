from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
import os
import time
from urllib.parse import urlparse
import re

class MusinsaCrawler:
    def __init__(self, download_folder="musinsa_images"):
        """
        무신사 크롤러 초기화
        
        Args:
            download_folder (str): 이미지를 저장할 폴더명
        """
        self.download_folder = download_folder
        self.driver = None
        self.setup_driver()
        self.create_download_folder()
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # ChromeDriver 경로 설정 (chromedriver가 PATH에 있거나 직접 경로 지정)
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"ChromeDriver 설정 오류: {e}")
            print("ChromeDriver를 다운로드하고 PATH에 추가하거나 Service를 사용하여 경로를 지정하세요.")
            raise
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def create_download_folder(self):
        """다운로드 폴더 생성"""
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            print(f"다운로드 폴더 생성: {self.download_folder}")
    
    def login(self, username, password):
        """
        무신사 로그인
        
        Args:
            username (str): 사용자명 (이메일 또는 아이디)
            password (str): 비밀번호
        """
        try:
            print("로그인 페이지로 이동 중...")
            self.driver.get("https://www.musinsa.com/auth/login?referer=https%3A%2F%2Fwww.musinsa.com%2Fmain%2Fmusinsa%2Frecommend%3Fgf%3DA")
            
            # 페이지 로드 대기
            time.sleep(3)
            
            # 아이디 입력
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "id"))
            )
            username_field.clear()
            username_field.send_keys(username)
            
            # 비밀번호 입력
            password_field = self.driver.find_element(By.NAME, "pw")
            password_field.clear()
            password_field.send_keys(password)
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # 로그인 완료 대기
            time.sleep(5)
            
            # 로그인 성공 확인
            if "login" not in self.driver.current_url:
                print("로그인 성공!")
                return True
            else:
                print("로그인 실패. 아이디/비밀번호를 확인하세요.")
                return False
                
        except Exception as e:
            print(f"로그인 중 오류 발생: {e}")
            return False
    
    def navigate_to_order_history(self):
        """구매 내역 페이지로 이동"""
        try:
            print("구매 내역 페이지로 이동 중...")
            self.driver.get("https://www.musinsa.com/order/order-list")
            time.sleep(3)
            
            # 페이지 로드 확인
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print("구매 내역 페이지 로드 완료")
            return True
            
        except Exception as e:
            print(f"구매 내역 페이지 이동 중 오류: {e}")
            return False
    
    def get_product_images(self):
        """구매 내역에서 상품 이미지 URL 수집"""
        image_urls = []
        
        try:
            # 페이지 스크롤하여 모든 내용 로드
            self.scroll_page()
            
            # 상품 이미지 요소 찾기 (무신사의 구매내역 페이지 구조에 따라 셀렉터 조정 필요)
            image_selectors = [
                "img[src*='image.msscdn.net']",  # 무신사 CDN 이미지
                ".order-item img",  # 주문 아이템 이미지
                ".product-img img",  # 상품 이미지
                ".thumb img",  # 썸네일 이미지
                "img[alt*='상품']",  # alt 텍스트에 '상품'이 포함된 이미지
            ]
            
            for selector in image_selectors:
                try:
                    images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for img in images:
                        src = img.get_attribute('src')
                        if src and self.is_valid_image_url(src):
                            image_urls.append(src)
                except Exception as e:
                    continue
            
            # 중복 제거
            image_urls = list(set(image_urls))
            print(f"총 {len(image_urls)}개의 이미지 URL을 찾았습니다.")
            
            return image_urls
            
        except Exception as e:
            print(f"이미지 URL 수집 중 오류: {e}")
            return []
    
    def is_valid_image_url(self, url):
        """유효한 이미지 URL인지 확인"""
        if not url or url.startswith('data:'):
            return False
        
        # 무신사 관련 도메인 및 이미지 확장자 확인
        valid_domains = ['msscdn.net', 'musinsa.com']
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        
        try:
            parsed_url = urlparse(url)
            domain_check = any(domain in parsed_url.netloc for domain in valid_domains)
            extension_check = any(ext in url.lower() for ext in valid_extensions)
            
            return domain_check and extension_check
        except:
            return False
    
    def scroll_page(self):
        """페이지를 스크롤하여 모든 콘텐츠 로드"""
        print("페이지 스크롤 중...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # 페이지 끝까지 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 새로운 높이 확인
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            last_height = new_height
        
        # 맨 위로 스크롤
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    
    def download_images(self, image_urls):
        """이미지 다운로드"""
        print(f"{len(image_urls)}개의 이미지 다운로드 시작...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.musinsa.com/'
        }
        
        downloaded_count = 0
        
        for i, url in enumerate(image_urls, 1):
            try:
                # URL에서 파일명 추출
                filename = self.get_filename_from_url(url, i)
                filepath = os.path.join(self.download_folder, filename)
                
                # 이미 존재하는 파일은 건너뛰기
                if os.path.exists(filepath):
                    print(f"[{i}/{len(image_urls)}] 이미 존재: {filename}")
                    continue
                
                # 이미지 다운로드
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # 파일 저장
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                downloaded_count += 1
                print(f"[{i}/{len(image_urls)}] 다운로드 완료: {filename}")
                
                # 서버 부하 방지를 위한 대기
                time.sleep(0.5)
                
            except Exception as e:
                print(f"[{i}/{len(image_urls)}] 다운로드 실패: {url} - {e}")
                continue
        
        print(f"다운로드 완료: {downloaded_count}개 파일")
        return downloaded_count
    
    def get_filename_from_url(self, url, index):
        """URL에서 파일명 추출"""
        try:
            # URL에서 파일명 추출
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # 파일명이 없거나 확장자가 없는 경우
            if not filename or '.' not in filename:
                # URL에서 확장자 추측
                if 'webp' in url:
                    ext = '.webp'
                elif 'png' in url:
                    ext = '.png'
                elif 'gif' in url:
                    ext = '.gif'
                else:
                    ext = '.jpg'
                
                filename = f"musinsa_product_{index:03d}{ext}"
            
            # 특수 문자 제거
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            return filename
            
        except:
            return f"musinsa_product_{index:03d}.jpg"
    
    def run(self, username, password):
        """전체 크롤링 프로세스 실행"""
        try:
            print("=== 무신사 구매내역 이미지 크롤링 시작 ===")
            
            # 1. 로그인
            if not self.login(username, password):
                return False
            
            # 2. 구매 내역 페이지 이동
            if not self.navigate_to_order_history():
                return False
            
            # 3. 이미지 URL 수집
            image_urls = self.get_product_images()
            
            if not image_urls:
                print("수집된 이미지가 없습니다.")
                return False
            
            # 4. 이미지 다운로드
            downloaded_count = self.download_images(image_urls)
            
            print(f"=== 크롤링 완료: {downloaded_count}개 이미지 저장 ===")
            return True
            
        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")
            return False
        
        finally:
            self.close()
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            print("브라우저 종료")

# 사용 예시
if __name__ == "__main__":
    # 사용자 정보 입력
    USERNAME = input("무신사 아이디/이메일 입력: ")
    PASSWORD = input("비밀번호 입력: ")
    
    # 크롤러 실행
    crawler = MusinsaCrawler("musinsa_purchase_images")
    crawler.run(USERNAME, PASSWORD)