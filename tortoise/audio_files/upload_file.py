import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_s3(file_name, bucket, object_name=None):
    """
    파일을 지정한 S3 버킷에 업로드하는 함수

    :param file_name: 로컬 파일 경로
    :param bucket: S3 버킷 이름
    :param object_name: S3에 저장할 파일 이름 (생략 시 로컬 파일 이름 사용)
    :return: True if file was uploaded, else False
    """
    # object_name이 없을 경우, file_name을 object_name으로 설정
    if object_name is None:
        object_name = file_name

    # S3 클라이언트 생성
    s3_client = boto3.client('s3')

    try:
        # 파일 업로드
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"파일 {file_name}을(를) {bucket}/{object_name}에 성공적으로 업로드했습니다.")
        return True
    except FileNotFoundError:
        print(f"파일 {file_name}을(를) 찾을 수 없습니다.")
        return False
    except NoCredentialsError:
        print("AWS 자격 증명을 찾을 수 없습니다.")
        return False

# 사용 예시
file_name = 'deniro.wav'  # 업로드할 파일 경로
bucket_name = 'dlgksruf'  # S3 버킷 이름
upload_to_s3(file_name, bucket_name)

