# 유틸리티 스크립트 모음
import os
import json
import shutil
from PIL import Image
import hashlib
from collections import defaultdict
from datetime import datetime

class ImageAnalyzer:
    """다운로드된 이미지 분석 및 관리 도구"""
    
    def __init__(self, folder_path):
        self.folder_path = folder_path
        
    def analyze_images(self):
        """이미지 분석 실행"""
        if not os.path.exists(self.folder_path):
            print(f"폴더가 존재하지 않습니다: {self.folder_path}")
            return
        
        print(f"=== {self.folder_path} 이미지 분석 ===")
        
        # 기본 통계
        stats = self.get_basic_stats()
        self.print_stats(stats)
        
        # 중복 이미지 찾기
        duplicates = self.find_duplicates()
        if duplicates:
            print(f"\n중복 이미지 발견: {len(duplicates)}쌍")
            self.handle_duplicates(duplicates)
        
        # 손상된 이미지 찾기
        corrupted = self.find_corrupted_images()
        if corrupted:
            print(f"\n손상된 이미지 발견: {len(corrupted)}개")
            self.handle_corrupted_images(corrupted)
        
        # 크기별 분류
        size_groups = self.group_by_size()
        self.print_size_distribution(size_groups)
        
    def get_basic_stats(self):
        """기본 통계 수집"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'extensions': defaultdict(int),
            'sizes': [],
            'dimensions': []
        }
        
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                filepath = os.path.join(self.folder_path, filename)
                
                # 파일 크기
                file_size = os.path.getsize(filepath)
                stats['total_files'] += 1
                stats['total_size'] += file_size
                stats['sizes'].append(file_size)
                
                # 확장자
                ext = os.path.splitext(filename)[1].lower()
                stats['extensions'][ext] += 1
                
                # 이미지 크기 (해상도)
                try:
                    with Image.open(filepath) as img:
                        stats['dimensions'].append(img.size)
                except Exception:
                    pass
        
        return stats
    
    def print_stats(self, stats):
        """통계 출력"""
        print(f"총 이미지 수: {stats['total_files']:,}개")
        print(f"총 용량: {stats['total_size']:,} bytes ({stats['total_size']/1024/1024:.1f} MB)")
        
        if stats['sizes']:
            print(f"평균 파일 크기: {sum(stats['sizes'])/len(stats['sizes']):,.0f} bytes")
            print(f"최대 파일 크기: {max(stats['sizes']):,} bytes")
            print(f"최소 파일 크기: {min(stats['sizes']):,} bytes")
        
        print("\n확장자별 분포:")
        for ext, count in stats['extensions'].items():
            percentage = (count / stats['total_files']) * 100
            print(f"  {ext}: {count:,}개 ({percentage:.1f}%)")
        
        if stats['dimensions']:
            print(f"\n해상도 정보:")
            widths = [d[0] for d in stats['dimensions']]
            heights = [d[1] for d in stats['dimensions']]
            print(f"  평균 해상도: {sum(widths)/len(widths):.0f} x {sum(heights)/len(heights):.0f}")
            print(f"  최대 해상도: {max(widths)} x {max(heights)}")
            print(f"  최소 해상도: {min(widths)} x {min(heights)}")
    
    def find_duplicates(self):
        """중복 이미지 찾기 (해시 기반)"""
        print("\n중복 이미지 검사 중...")
        hash_dict = defaultdict(list)
        
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                filepath = os.path.join(self.folder_path, filename)
                
                try:
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        hash_dict[file_hash].append(filename)
                except Exception as e:
                    print(f"해시 계산 실패: {filename} - {e}")
        
        # 중복 파일만 반환
        duplicates = {k: v for k, v in hash_dict.items() if len(v) > 1}
        return duplicates
    
    def handle_duplicates(self, duplicates):
        """중복 이미지 처리"""
        print("\n중복 이미지 목록:")
        for file_hash, files in duplicates.items():
            print(f"  해시 {file_hash[:8]}...: {files}")
        
        choice = input("\n중복 파일을 자동으로 정리하시겠습니까? (y/N): ").lower()
        if choice == 'y':
            removed_count = 0
            for file_hash, files in duplicates.items():
                # 첫 번째 파일은 유지하고 나머지 삭제
                files_to_remove = files[1:]
                for filename in files_to_remove:
                    filepath = os.path.join(self.folder_path, filename)
                    try:
                        os.remove(filepath)
                        removed_count += 1
                        print(f"삭제: {filename}")
                    except Exception as e:
                        print(f"삭제 실패: {filename} - {e}")
            
            print(f"총 {removed_count}개 중복 파일 삭제 완료")
    
    def find_corrupted_images(self):
        """손상된 이미지 찾기"""
        print("\n손상된 이미지 검사 중...")
        corrupted = []
        
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                filepath = os.path.join(self.folder_path, filename)
                
                try:
                    with Image.open(filepath) as img:
                        img.verify()  # 이미지 무결성 검사
                except Exception as e:
                    corrupted.append((filename, str(e)))
        
        return corrupted
    
    def handle_corrupted_images(self, corrupted):
        """손상된 이미지 처리"""
        print("\n손상된 이미지 목록:")
        for filename, error in corrupted:
            print(f"  {filename}: {error}")
        
        choice = input("\n손상된 이미지를 삭제하시겠습니까? (y/N): ").lower()
        if choice == 'y':
            removed_count = 0
            for filename, error in corrupted:
                filepath = os.path.join(self.folder_path, filename)
                try:
                    os.remove(filepath)
                    removed_count += 1
                    print(f"삭제: {filename}")
                except Exception as e:
                    print(f"삭제 실패: {filename} - {e}")
            
            print(f"총 {removed_count}개 손상된 파일 삭제 완료")
    
    def group_by_size(self):
        """크기별 이미지 분류"""
        size_groups = {
            'small': [],    # < 100KB
            'medium': [],   # 100KB - 1MB
            'large': [],    # 1MB - 5MB
            'xlarge': []    # > 5MB
        }
        
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                filepath = os.path.join(self.folder_path, filename)
                file_size = os.path.getsize(filepath)
                
                if file_size < 100 * 1024:  # 100KB
                    size_groups['small'].append(filename)
                elif file_size < 1024 * 1024:  # 1MB
                    size_groups['medium'].append(filename)
                elif file_size < 5 * 1024 * 1024:  # 5MB
                    size_groups['large'].append(filename)
                else:
                    size_groups['xlarge'].append(filename)
        
        return size_groups
    
    def print_size_distribution(self, size_groups):
        """크기 분포 출력"""
        print("\n파일 크기 분포:")
        print(f"  소형 (< 100KB): {len(size_groups['small'])}개")
        print(f"  중형 (100KB - 1MB): {len(size_groups['medium'])}개")
        print(f"  대형 (1MB - 5MB): {len(size_groups['large'])}개")
        print(f"  초대형 (> 5MB): {len(size_groups['xlarge'])}개")

class ImageOrganizer:
    """이미지 정리 및 분류 도구"""
    
    def __init__(self, source_folder):
        self.source_folder = source_folder
    
    def organize_by_brand(self):
        """브랜드별로 폴더 정리"""
        if not os.path.exists(self.source_folder):
            print(f"폴더가 존재하지 않습니다: {self.source_folder}")
            return
        
        print("브랜드별 폴더 정리 중...")
        organized_folder = f"{self.source_folder}_organized"
        
        if not os.path.exists(organized_folder):
            os.makedirs(organized_folder)
        
        brand_counts = defaultdict(int)
        
        for filename in os.listdir(self.source_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                # 파일명에서 브랜드 추출 시도
                brand = self.extract_brand_from_filename(filename)
                
                brand_folder = os.path.join(organized_folder, brand)
                if not os.path.exists(brand_folder):
                    os.makedirs(brand_folder)
                
                source_path = os.path.join(self.source_folder, filename)
                dest_path = os.path.join(brand_folder, filename)
                
                try:
                    shutil.copy2(source_path, dest_path)
                    brand_counts[brand] += 1
                except Exception as e:
                    print(f"파일 복사 실패: {filename} - {e}")
        
        print(f"\n브랜드별 정리 완료: {organized_folder}")
        print("브랜드별 이미지 수:")
        for brand, count in sorted(brand_counts.items()):
            print(f"  {brand}: {count}개")
    
    def extract_brand_from_filename(self, filename):
        """파일명에서 브랜드명 추출"""
        # 파일명 패턴: musinsa_brand_productid_001.jpg
        parts = filename.split('_')
        
        if len(parts) >= 2 and parts[0] == 'musinsa':
            return parts[1] if parts[1] != 'product' else 'unknown'
        
        return 'unknown'
    
    def organize_by_date(self):
        """생성일자별로 폴더 정리"""
        if not os.path.exists(self.source_folder):
            print(f"폴더가 존재하지 않습니다: {self.source_folder}")
            return
        
        print("날짜별 폴더 정리 중...")
        organized_folder = f"{self.source_folder}_by_date"
        
        if not os.path.exists(organized_folder):
            os.makedirs(organized_folder)
        
        for filename in os.listdir(self.source_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                filepath = os.path.join(self.source_folder, filename)
                
                # 파일 생성일자 가져오기
                creation_time = os.path.getctime(filepath)
                date_str = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d")
                
                date_folder = os.path.join(organized_folder, date_str)
                if not os.path.exists(date_folder):
                    os.makedirs(date_folder)
                
                dest_path = os.path.join(date_folder, filename)
                
                try:
                    shutil.copy2(filepath, dest_path)
                except Exception as e:
                    print(f"파일 복사 실패: {filename} - {e}")
        
        print(f"날짜별 정리 완료: {organized_folder}")

class ImageConverter:
    """이미지 형식 변환 도구"""
    
    def __init__(self, source_folder):
        self.source_folder = source_folder
    
    def convert_to_jpg(self, quality=85):
        """모든 이미지를 JPG로 변환"""
        if not os.path.exists(self.source_folder):
            print(f"폴더가 존재하지 않습니다: {self.source_folder}")
            return
        
        converted_folder = f"{self.source_folder}_jpg"
        if not os.path.exists(converted_folder):
            os.makedirs(converted_folder)
        
        converted_count = 0
        
        for filename in os.listdir(self.source_folder):
            if filename.lower().endswith(('.png', '.webp', '.gif')):
                source_path = os.path.join(self.source_folder, filename)
                
                # 새 파일명 (확장자를 .jpg로 변경)
                name_without_ext = os.path.splitext(filename)[0]
                new_filename = f"{name_without_ext}.jpg"
                dest_path = os.path.join(converted_folder, new_filename)
                
                try:
                    with Image.open(source_path) as img:
                        # RGBA를 RGB로 변환 (PNG 투명도 처리)
                        if img.mode in ('RGBA', 'LA', 'P'):
                            # 흰색 배경으로 변환
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background
                        
                        img.save(dest_path, 'JPEG', quality=quality, optimize=True)
                        converted_count += 1
                        print(f"변환 완료: {filename} → {new_filename}")
                        
                except Exception as e:
                    print(f"변환 실패: {filename} - {e}")
            
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                # JPG 파일은 그대로 복사
                source_path = os.path.join(self.source_folder, filename)
                dest_path = os.path.join(converted_folder, filename)
                try:
                    shutil.copy2(source_path, dest_path)
                except Exception as e:
                    print(f"복사 실패: {filename} - {e}")
        
        print(f"\nJPG 변환 완료: {converted_count}개 파일")
        print(f"저장 위치: {converted_folder}")
    
    def resize_images(self, max_width=1920, max_height=1080, quality=85):
        """이미지 크기 조정"""
        if not os.path.exists(self.source_folder):
            print(f"폴더가 존재하지 않습니다: {self.source_folder}")
            return
        
        resized_folder = f"{self.source_folder}_resized"
        if not os.path.exists(resized_folder):
            os.makedirs(resized_folder)
        
        resized_count = 0
        
        for filename in os.listdir(self.source_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                source_path = os.path.join(self.source_folder, filename)
                dest_path = os.path.join(resized_folder, filename)
                
                try:
                    with Image.open(source_path) as img:
                        original_size = img.size
                        
                        # 비율 유지하면서 크기 조정
                        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                        
                        # 파일 형식에 따라 저장
                        if filename.lower().endswith(('.jpg', '.jpeg')):
                            img.save(dest_path, 'JPEG', quality=quality, optimize=True)
                        elif filename.lower().endswith('.png'):
                            img.save(dest_path, 'PNG', optimize=True)
                        elif filename.lower().endswith('.webp'):
                            img.save(dest_path, 'WEBP', quality=quality, optimize=True)
                        
                        if img.size != original_size:
                            resized_count += 1
                            print(f"크기 조정: {filename} {original_size} → {img.size}")
                        else:
                            print(f"크기 유지: {filename} {original_size}")
                        
                except Exception as e:
                    print(f"크기 조정 실패: {filename} - {e}")
        
        print(f"\n크기 조정 완료: {resized_count}개 파일")
        print(f"저장 위치: {resized_folder}")

# 통합 관리 도구
class MusinsaImageManager:
    """무신사 이미지 통합 관리 도구"""
    
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.analyzer = ImageAnalyzer(folder_path)
        self.organizer = ImageOrganizer(folder_path)
        self.converter = ImageConverter(folder_path)
    
    def run_interactive_menu(self):
        """대화형 메뉴 실행"""
        while True:
            print("\n=== 무신사 이미지 관리 도구 ===")
            print(f"대상 폴더: {self.folder_path}")
            print("\n1. 이미지 분석")
            print("2. 브랜드별 정리")
            print("3. 날짜별 정리")
            print("4. JPG 변환")
            print("5. 이미지 크기 조정")
            print("6. 전체 최적화 (분석 + 정리 + 변환)")
            print("0. 종료")
            
            choice = input("\n원하는 작업을 선택하세요 (0-6): ").strip()
            
            if choice == '0':
                print("프로그램을 종료합니다.")
                break
            elif choice == '1':
                self.analyzer.analyze_images()
            elif choice == '2':
                self.organizer.organize_by_brand()
            elif choice == '3':
                self.organizer.organize_by_date()
            elif choice == '4':
                quality = input("JPG 품질 (1-100, 기본값 85): ").strip()
                quality = int(quality) if quality.isdigit() and 1 <= int(quality) <= 100 else 85
                self.converter.convert_to_jpg(quality)
            elif choice == '5':
                width = input("최대 너비 (기본값 1920): ").strip()
                height = input("최대 높이 (기본값 1080): ").strip()
                quality = input("품질 (1-100, 기본값 85): ").strip()
                
                width = int(width) if width.isdigit() else 1920
                height = int(height) if height.isdigit() else 1080
                quality = int(quality) if quality.isdigit() and 1 <= int(quality) <= 100 else 85
                
                self.converter.resize_images(width, height, quality)
            elif choice == '6':
                print("전체 최적화 실행 중...")
                self.analyzer.analyze_images()
                self.organizer.organize_by_brand()
                self.converter.convert_to_jpg()
                print("전체 최적화 완료!")
            else:
                print("잘못된 선택입니다. 다시 선택해주세요.")

# 명령줄 도구
def main():
    """메인 실행 함수"""
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python image_utils.py <이미지_폴더_경로>")
        print("예시: python image_utils.py ./musinsa_images_20240805_143022")
        return
    
    folder_path = sys.argv[1]
    
    if not os.path.exists(folder_path):
        print(f"폴더가 존재하지 않습니다: {folder_path}")
        return
    
    manager = MusinsaImageManager(folder_path)
    manager.run_interactive_menu()

if __name__ == "__main__":
    main()