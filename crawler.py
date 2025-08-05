from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import time
from urllib.parse import urlparse
import re
import json
from datetime import datetime

class AdvancedMusinsaCrawler:
    def __init__(self, download_folder="musinsa_images", config_file="crawler_config.json"):
        """
        고급 무신사 크롤러 초기화
        
        Args:
            download_folder (str): 이미지를 저장할 폴더명
            config_file (str): 설정 파일명
        """
        self.download_folder = download_folder
        self.config_file = config_file
        self.driver = None
        self.config = self.load_config()
        self.setup_driver()
        self.create_download_folder()
        self.session_log = []
    
    def load_config(self):
        """설정 파일 로드"""
        default_config = {
            "max_images": 1000,
            "download_delay": 0.5,
            "page_load_timeout": 30,
            "implicit_wait": 10,
            "retry_attempts": 3,
            "image_quality_filter": True,
            "headless_mode": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"설정 파일 로드 오류: {e}, 기본 설정 사용")
        
        return default_config
    
    def save_config(self):
        """설정 파일 저장"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def setup_driver(self):
        """Chrome 드라이버 자동 설정"""
        try:
            chrome_options = Options()
            
            if self.config.get("headless_mode", False):
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # 브라우저에서 이미지 로드 비활성화로 속도 향상
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # ChromeDriver 자동 다운로드 및 설정
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 웹드라이버 탐지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 타임아웃 설정
            self.driver.implicitly_wait(self.config.get("implicit_wait", 10))
            self.driver.set_page_load_timeout(self.config.get("page_load_timeout", 30))
            
            print("ChromeDriver 설정 완료")
            
        except Exception as e:
            print(f"ChromeDriver 설정 오류: {e}")
            raise
    
    def create_download_folder(self):
        """다운로드 폴더 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.download_folder = f"{self.download_folder}_{timestamp}"
        
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            print(f"다운로드 폴더 생성: {self.download_folder}")
    
    def login_with_retry(self, username, password):
        """재시도 로직이 있는 로그인"""
        max_attempts = self.config.get("retry_attempts", 3)
        
        for attempt in range(max_attempts):
            try:
                print(f"로그인 시도 {attempt + 1}/{max_attempts}")
                
                self.driver.get("https://www.musinsa.com/auth/login")
                time.sleep(2)
                
                # 아이디 입력
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "id"))
                )
                username_field.clear()
                username_field.send_keys(username)
                
                # 비밀번호 입력
                password_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "pw"))
                )
                password_field.clear()
                password_field.send_keys(password)
                
                # 로그인 버튼 클릭
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )
                login_button.click()
                
                # 로그인 결과 대기
                time.sleep(5)
                
                # 로그인 성공 확인
                if self.is_logged_in():
                    print("로그인 성공!")
                    self.log_session("로그인 성공")
                    return True
                else:
                    print(f"로그인 실패 (시도 {attempt + 1})")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
                    
            except Exception as e:
                print(f"로그인 시도 {attempt + 1} 중 오류: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(5)
        
        print("모든 로그인 시도 실패")
        return False
    
    def is_logged_in(self):
        """로그인 상태 확인"""
        try:
            # 로그인 후 리다이렉트 또는 특정 요소 존재 확인
            current_url = self.driver.current_url
            
            # 로그인 페이지가 아니거나 마이페이지 관련 요소가 있으면 로그인 성공
            if "login" not in current_url or "auth" not in current_url:
                return True
            
            # 추가 확인: 사용자 정보나 로그아웃 버튼 존재 확인
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='logout']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".user-info")),
                        EC.presence_of_element_located((By.LINK_TEXT, "마이페이지"))
                    )
                )
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"로그인 상태 확인 오류: {e}")
            return False
    
    def navigate_to_order_history_with_pagination(self):
        """구매 내역 페이지로 이동 및 페이지네이션 처리"""
        try:
            print("구매 내역 페이지로 이동 중...")
            self.driver.get("https://www.musinsa.com/order/order-list")
            
            # 페이지 로드 대기
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)
            
            # 더보기 버튼이나 페이지네이션 처리
            self.load_all_order_pages()
            
            print("모든 구매 내역 페이지 로드 완료")
            return True
            
        except Exception as e:
            print(f"구매 내역 페이지 이동 중 오류: {e}")
            return False
    
    def load_all_order_pages(self):
        """모든 구매 내역 페이지 로드"""
        max_pages = 50  # 최대 페이지 제한
        current_page = 1
        
        while current_page <= max_pages:
            try:
                print(f"페이지 {current_page} 로드 중...")
                
                # 페이지 끝까지 스크롤
                self.scroll_to_bottom()
                
                # "더보기" 버튼 찾기
                more_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button:contains('더보기'), .more-btn, [data-testid='more'], .load-more")
                
                if more_buttons:
                    for btn in more_buttons:
                        try:
                            if btn.is_displayed() and btn.is_enabled():
                                self.driver.execute_script("arguments[0].click();", btn)
                                time.sleep(3)
                                break
                        except:
                            continue
                else:
                    # 페이지네이션 번호로 시도
                    next_page_link = self.driver.find_elements(By.CSS_SELECTOR, 
                        f"a[href*='page={current_page + 1}'], .pagination a:contains('{current_page + 1}')")
                    
                    if next_page_link:
                        try:
                            next_page_link[0].click()
                            time.sleep(3)
                        except:
                            break
                    else:
                        print("더 이상 로드할 페이지가 없습니다.")
                        break
                
                current_page += 1
                
            except Exception as e:
                print(f"페이지 {current_page} 로드 중 오류: {e}")
                break
    
    def scroll_to_bottom(self):
        """페이지 하단까지 스크롤"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def extract_product_images_advanced(self):
        """고급 상품 이미지 추출"""
        image_urls = set()
        
        try:
            print("상품 이미지 URL 추출 중...")
            
            # 다양한 이미지 셀렉터
            selectors = [
                # 무신사 특화 셀렉터
                "img[src*='image.msscdn.net']",
                "img[src*='image.musinsa.com']",
                "img[data-src*='image.msscdn.net']",
                
                # 일반적인 상품 이미지 셀렉터
                ".product-image img",
                ".item-image img",
                ".order-item img",
                ".product-thumb img",
                ".goods-thumb img",
                
                # 데이터 속성 기반
                "img[data-original*='msscdn']",
                "img[data-lazy*='msscdn']",
                
                # alt 텍스트 기반
                "img[alt*='상품']",
                "img[alt*='product']",
                "img[alt*='브랜드']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"셀렉터 '{selector}'로 {len(elements)}개 요소 발견")
                    
                    for element in elements:
                        # src, data-src, data-original 등 다양한 속성 확인
                        for attr in ['src', 'data-src', 'data-original', 'data-lazy']:
                            url = element.get_attribute(attr)
                            if url and self.is_valid_product_image(url):
                                # 고해상도 이미지로 변환 시도
                                high_res_url = self.convert_to_high_resolution(url)
                                image_urls.add(high_res_url)
                                
                except Exception as e:
                    print(f"셀렉터 '{selector}' 처리 중 오류: {e}")
                    continue
            
            # JavaScript로 추가 이미지 탐색
            try:
                js_images = self.driver.execute_script("""
                    const images = [];
                    const allImages = document.querySelectorAll('img');
                    allImages.forEach(img => {
                        const src = img.src || img.dataset.src || img.dataset.original;
                        if (src && (src.includes('msscdn.net') || src.includes('musinsa.com'))) {
                            images.push(src);
                        }
                    });
                    return images;
                """)
                
                for url in js_images:
                    if self.is_valid_product_image(url):
                        high_res_url = self.convert_to_high_resolution(url)
                        image_urls.add(high_res_url)
                        
            except Exception as e:
                print(f"JavaScript 이미지 추출 오류: {e}")
            
            final_urls = list(image_urls)
            print(f"총 {len(final_urls)}개의 고유 이미지 URL 발견")
            
            # 최대 이미지 수 제한 적용
            max_images = self.config.get("max_images", 1000)
            if len(final_urls) > max_images:
                final_urls = final_urls[:max_images]
                print(f"최대 이미지 수 제한으로 {max_images}개만 선택")
            
            return final_urls
            
        except Exception as e:
            print(f"이미지 추출 중 오류: {e}")
            return []
    
    def is_valid_product_image(self, url):
        """유효한 상품 이미지 URL인지 확인"""
        if not url or url.startswith('data:'):
            return False
        
        # 무신사 관련 도메인 확인
        valid_domains = ['msscdn.net', 'musinsa.com']
        invalid_patterns = ['logo', 'banner', 'ad', 'icon', 'sprite']
        
        try:
            url_lower = url.lower()
            
            # 도메인 확인
            domain_valid = any(domain in url_lower for domain in valid_domains)
            if not domain_valid:
                return False
            
            # 불필요한 이미지 패턴 제외
            if any(pattern in url_lower for pattern in invalid_patterns):
                return False
            
            # 이미지 확장자 확인
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            if not any(ext in url_lower for ext in valid_extensions):
                return False
            
            # 최소 크기 확인 (작은 아이콘 제외)
            if any(size in url_lower for size in ['16x16', '32x32', '50x50']):
                return False
            
            return True
            
        except Exception:
            return False
    
    def convert_to_high_resolution(self, url):
        """이미지를 고해상도 버전으로 변환"""
        try:
            # 무신사 이미지 URL 패턴에 따른 고해상도 변환
            # 예: thumb -> large, small -> origin 등
            conversions = {
                '/thumb/': '/large/',
                '/small/': '/origin/',
                '_thumb': '_large',
                '_small': '_origin',
                '/150/': '/500/',
                '/300/': '/800/',
                '_150.': '_500.',
                '_300.': '_800.'
            }
            
            high_res_url = url
            for old, new in conversions.items():
                if old in url:
                    high_res_url = url.replace(old, new)
                    break
            
            return high_res_url
            
        except Exception:
            return url
    
    def download_images_with_progress(self, image_urls):
        """진행률 표시와 함께 이미지 다운로드"""
        if not image_urls:
            print("다운로드할 이미지가 없습니다.")
            return 0
        
        print(f"{len(image_urls)}개 이미지 다운로드 시작...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.musinsa.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }
        
        downloaded_count = 0
        failed_count = 0
        download_info = []
        
        for i, url in enumerate(image_urls, 1):
            try:
                filename = self.generate_filename(url, i)
                filepath = os.path.join(self.download_folder, filename)
                
                # 이미 존재하는 파일 확인
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    if file_size > 1024:  # 1KB 이상이면 유효한 파일로 간주
                        print(f"[{i:3d}/{len(image_urls)}] 건너뛰기: {filename}")
                        continue
                
                # 이미지 다운로드
                response = requests.get(url, headers=headers, timeout=15, stream=True)
                response.raise_for_status()
                
                # Content-Type 확인
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    print(f"[{i:3d}/{len(image_urls)}] 이미지가 아님: {filename}")
                    failed_count += 1
                    continue
                
                # 파일 저장
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(filepath)
                
                # 품질 필터링
                if self.config.get("image_quality_filter", True) and file_size < 5120:  # 5KB 미만
                    os.remove(filepath)
                    print(f"[{i:3d}/{len(image_urls)}] 품질 낮음: {filename}")
                    failed_count += 1
                    continue
                
                downloaded_count += 1
                download_info.append({
                    'filename': filename,
                    'url': url,
                    'size': file_size,
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"[{i:3d}/{len(image_urls)}] 완료: {filename} ({file_size:,} bytes)")
                
                # 다운로드 지연
                time.sleep(self.config.get("download_delay", 0.5))
                
            except requests.exceptions.RequestException as e:
                print(f"[{i:3d}/{len(image_urls)}] 네트워크 오류: {e}")
                failed_count += 1
                continue
                
            except Exception as e:
                print(f"[{i:3d}/{len(image_urls)}] 다운로드 실패: {e}")
                failed_count += 1
                continue
        
        # 다운로드 정보 저장
        self.save_download_info(download_info)
        
        print(f"\n=== 다운로드 완료 ===")
        print(f"성공: {downloaded_count}개")
        print(f"실패: {failed_count}개")
        print(f"전체: {len(image_urls)}개")
        
        return downloaded_count
    
    def generate_filename(self, url, index):
        """고급 파일명 생성"""
        try:
            parsed_url = urlparse(url)
            original_name = os.path.basename(parsed_url.path)
            
            # URL에서 상품 ID나 브랜드 정보 추출 시도
            path_parts = parsed_url.path.split('/')
            brand_info = ""
            product_id = ""
            
            for part in path_parts:
                if part.isdigit() and len(part) >= 6:  # 상품 ID로 추정
                    product_id = part
                elif part and not part.isdigit() and len(part) > 2:  # 브랜드명으로 추정
                    brand_info = part[:20]  # 최대 20자
            
            # 확장자 결정
            if original_name and '.' in original_name:
                name, ext = os.path.splitext(original_name)
            else:
                ext = '.jpg'  # 기본 확장자
                if 'webp' in url.lower():
                    ext = '.webp'
                elif 'png' in url.lower():
                    ext = '.png'
            
            # 파일명 조합
            if product_id and brand_info:
                filename = f"musinsa_{brand_info}_{product_id}_{index:03d}{ext}"
            elif product_id:
                filename = f"musinsa_product_{product_id}_{index:03d}{ext}"
            elif original_name:
                filename = f"musinsa_{index:03d}_{original_name}"
            else:
                filename = f"musinsa_image_{index:03d}{ext}"
            
            # 파일명 정리
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filename = re.sub(r'_{2,}', '_', filename)  # 연속 언더스코어 제거
            
            return filename
            
        except Exception:
            return f"musinsa_image_{index:03d}.jpg"
    
    def save_download_info(self, download_info):
        """다운로드 정보를 JSON 파일로 저장"""
        try:
            info_file = os.path.join(self.download_folder, "download_info.json")
            
            summary = {
                'download_date': datetime.now().isoformat(),
                'total_images': len(download_info),
                'total_size_bytes': sum(item['size'] for item in download_info),
                'config_used': self.config,
                'images': download_info
            }
            
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"다운로드 정보 저장: {info_file}")
            
        except Exception as e:
            print(f"다운로드 정보 저장 실패: {e}")
    
    def log_session(self, message):
        """세션 로그 기록"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        self.session_log.append(log_entry)
    
    def save_session_log(self):
        """세션 로그 저장"""
        try:
            log_file = os.path.join(self.download_folder, "session_log.json")
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"세션 로그 저장 실패: {e}")
    
    def run_advanced(self, username, password):
        """고급 크롤링 프로세스 실행"""
        try:
            print("=== 무신사 고급 구매내역 이미지 크롤링 시작 ===")
            print(f"설정: {self.config}")
            
            self.log_session("크롤링 시작")
            
            # 1. 로그인
            if not self.login_with_retry(username, password):
                self.log_session("로그인 실패")
                return False
            
            # 2. 구매 내역 페이지 이동 및 모든 페이지 로드
            if not self.navigate_to_order_history_with_pagination():
                self.log_session("구매 내역 페이지 로드 실패")
                return False
            
            # 3. 고급 이미지 추출
            image_urls = self.extract_product_images_advanced()
            
            if not image_urls:
                print("추출된 이미지가 없습니다.")
                self.log_session("이미지 추출 실패 - 이미지 없음")
                return False
            
            self.log_session(f"{len(image_urls)}개 이미지 URL 추출 완료")
            
            # 4. 이미지 다운로드
            downloaded_count = self.download_images_with_progress(image_urls)
            
            if downloaded_count > 0:
                self.log_session(f"다운로드 완료: {downloaded_count}개 이미지")
                print(f"\n=== 크롤링 성공 완료 ===")
                print(f"저장 위치: {self.download_folder}")
                print(f"다운로드된 이미지: {downloaded_count}개")
                return True
            else:
                self.log_session("다운로드 실패")
                return False
                
        except KeyboardInterrupt:
            print("\n사용자에 의해 중단되었습니다.")
            self.log_session("사용자 중단")
            return False
            
        except Exception as e:
            print(f"크롤링 중 예상치 못한 오류: {e}")
            self.log_session(f"오류 발생: {str(e)}")
            return False
        
        finally:
            self.save_session_log()
            self.close()
    
    def close(self):
        """리소스 정리"""
        if self.driver:
            try:
                self.driver.quit()
                print("브라우저 종료 완료")
            except Exception as e:
                print(f"브라우저 종료 중 오류: {e}")

# 설정 파일 생성 함수
def create_config_file():
    """설정 파일 생성"""
    config = {
        "max_images": 1000,
        "download_delay": 0.5,
        "page_load_timeout": 30,
        "implicit_wait": 10,
        "retry_attempts": 3,
        "image_quality_filter": True,
        "headless_mode": False
    }
    
    with open("crawler_config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("설정 파일 'crawler_config.json' 생성 완료")
    print("필요에 따라 설정을 수정하세요:")
    print("- max_images: 최대 다운로드 이미지 수")
    print("- download_delay: 다운로드 간 지연 시간(초)")
    print("- image_quality_filter: 저품질 이미지 필터링 여부")
    print("- headless_mode: 브라우저 창 숨김 여부")

# 메인 실행 함수
def main():
    """메인 실행 함수"""
    print("=== 무신사 구매내역 이미지 크롤러 ===")
    
    # 설정 파일이 없으면 생성
    if not os.path.exists("crawler_config.json"):
        create_config_file()
        print("\n설정 파일이 생성되었습니다. 필요시 수정 후 다시 실행하세요.")
        return
    
    try:
        # 사용자 입력
        print("\n로그인 정보를 입력하세요:")
        username = input("무신사 아이디/이메일: ").strip()
        password = input("비밀번호: ").strip()
        
        if not username or not password:
            print("아이디와 비밀번호를 모두 입력해야 합니다.")
            return
        
        # 크롤러 실행
        crawler = AdvancedMusinsaCrawler()
        success = crawler.run_advanced(username, password)
        
        if success:
            print("\n크롤링이 성공적으로 완료되었습니다!")
        else:
            print("\n크롤링 중 문제가 발생했습니다.")
            
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()