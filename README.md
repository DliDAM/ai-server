## DliDAM AI-Server <img src="https://raw.githubusercontent.com/MartinHeinz/MartinHeinz/master/wave.gif" width="30px">

### 1. 서비스 소개
청각 장애인들은 일상적인 소통에서 다양한 어려움을 겪고 있습니다. 기존의 문자나 비주얼 기반 소통 도구들이 있지만, 이들 도구는 음성 소통이 가진 즉각성과 몰입감을 전달하기에는 한계가 있습니다. 특히 청각 장애인의 목소리를 직접 듣지 못한 타인은 그들의 의사소통 방식에 익숙하지 않아 의사 전달에 장애가 생기곤 합니다. 이러한 배경에서 "들리담"은 청각 장애인들이 자신만의 고유한 음성을 활용해 보다 편리하고 자연스러운 소통을 할 수 있는 방법을 제공하고자 기획되었습니다.

"들리담"은 청각 장애인을 위한 실시간 음성 통신 솔루션을 제공하는 애플리케이션입니다. 먼저 청각 장애인이 자신의 목소리를 초기에 등록하면, 들리담은 이 목소리를 학습하고 개인의 목소리 특성을 가중치로 저장합니다. 이후 청각 장애인이 채팅을 통해 의사소통을 할 때, 상대방은 실제 음성처럼 변조된 청각 장애인의 목소리를 듣게 됩니다. 이로써 청각 장애인이 보다 자연스럽고 개인화된 음성 소통을 할 수 있도록 지원하는 서비스입니다.

#### <a href="https://www.youtube.com/watch?v=FYObtRgW-n4">See Demo video here! 🎬</a>

### 2. 서비스 화면

|Login|Sign-up|Friend list|Search & Add friends|My profile|
|:---:|:---:|:---:|:---:|:---:|
|<img width="150" alt="login" src="https://github.com/user-attachments/assets/bc6c4b31-849a-4c25-8c7f-f716f403621c">|<img width="150" alt="signup" src="https://github.com/user-attachments/assets/7d0bf3ab-e343-4700-bf48-4c4a7dff7de5">|<img width="150" alt="friendlist" src="https://github.com/user-attachments/assets/d25b670a-2798-4544-a228-7262d89a4aa4">|<img width="150" alt="search and add" src="https://github.com/user-attachments/assets/203780ea-71ce-4787-a1a8-bdfaae02ce5f">|<img width="150" alt="search and add" src="https://github.com/user-attachments/assets/3201d532-7ff1-4dd5-aa90-e46cf93feb56">|

|Chat list|Chat room|Setting|Edit account info|User guide|
|:---:|:---:|:---:|:---:|:---:|
|<img width="150" alt="chatlist" src="https://github.com/user-attachments/assets/ec6d13ba-21fe-48a8-92d3-08d7d3ae81c8">|<img width="150" alt="chatroom" src="https://github.com/user-attachments/assets/39a6f2c7-8bed-432e-83a7-93d41c425acf">|<img width="150" alt="setting" src="https://github.com/user-attachments/assets/427f9ac9-5aa1-4169-b0bd-886ef676a35c">|<img width="150" alt="edit account" src="https://github.com/user-attachments/assets/8556c0bc-fe27-4e73-91f8-f879dbd71139">|<img width="150" alt="user guide" src="https://github.com/user-attachments/assets/0b9a68b7-e214-45d1-82dd-c046c46d032e">|


### 3. AI-Server 실행 방법

1. DliDAM/ai-server 다운로드

2. 가상환경 생성 및 활성화
```bash
conda create -n tortoise python=3.8
conda activate tortoise
```

3. main.py 실행
```bash
cd ai-server
cd tortoise
python main.py
```

### 4. 사용한 TTS 모델 및 한국어 Fine-tuning 방법
[![TorToise-tts](https://github.com/user-attachments/assets/b0af087d-ccd9-4579-9c6d-56051faae4d6)](https://github.com/neonbjb/tortoise-tts)
- Tortoise-tts
    - Multi-voice가 가능하고, 실제같은 prosody & intonation을 제공하는 TTS 프로그램
    - Autoregressive transformer & DDPM 기반의 이미지 생성 원리를 TTS에 적용(Joining Autoregressive Decoders & DDPM)
        - Autoregressive decoder: 텍스트에 따라 음성 토큰의 확률 분포 예측
        - CLIP과 유사한 contrastive 모델을 사용하여 Autoregressive decoder의 ouput ranking
        - DDPM: 음성 토큰을 다시 음성 spectogram으로 변환
- 한국어 Fine-tuning
    - Korean Single Speaker Speech Dataset 중 임의로 1,000개 데이터 사용
        - [데이터셋 링크](https://www.kaggle.com/datasets/bryanpark/korean-single-speaker-speech-dataset)
    - DL-Art-School를 사용하여 fine-tuning 후, HuggingFace에 fine-tuning한 모델의 가중치를 업로드하여 사용
        - [DL-Art-School repository](https://github.com/152334H/DL-Art-School)
