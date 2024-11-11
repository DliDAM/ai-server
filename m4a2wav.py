import os
from pydub import AudioSegment

def convert_m4a_to_wav(input_path):
    # 입력 경로의 모든 파일 검색
    for root, dirs, files in os.walk(input_path):
        for file in files:
            # m4a 파일만 처리
            if file.endswith('.m4a'):
                # 파일의 전체 경로
                m4a_path = os.path.join(root, file)
                # wav 파일명 생성 (확장자만 변경)
                wav_path = os.path.splitext(m4a_path)[0] + '.wav'
                
                try:
                    # m4a 파일 로드
                    audio = AudioSegment.from_file(m4a_path, format='m4a')
                    # wav 파일로 저장
                    audio.export(wav_path, format='wav')
                    print(f'변환 완료: {file}')
                except Exception as e:
                    print(f'변환 실패: {file} - {str(e)}')

if __name__ == "__main__":
    # 변환하고자 하는 폴더 경로 지정
    input_folder = "/Users/bangbyeonghun/Documents/projects/grad/ai-server/tortoise/tortoise/voices/rose"
    convert_m4a_to_wav(input_folder)
