const { spawn } = require('child_process');
const path = require('path');

// Python 스크립트의 경로
const pythonScriptPath = path.join(__dirname, 'test.py');

// 서버 IP와 포트 설정
const serverIp = 'localhost';
const serverPort = '5000';

// 전송할 텍스트
const textToConvert = "Hello, this is a test.";

// Output 파일 이름은 Python 스크립트와 일치하도록 지정합니다.
const characterName = "deniro";
const outputFile = `output_${characterName}_${textToConvert.length}.wav`;

// Python 프로세스를 실행합니다.
const pythonProcess = spawn('python', [pythonScriptPath, textToConvert, serverIp, serverPort]);

// Python 스크립트의 출력 및 오류를 처리합니다.
pythonProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
});

pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
});

pythonProcess.on('close', (code) => {
    console.log(`Python script exited with code: ${code}`);
    
    // .wav 파일이 생성되었는지 확인합니다.
    const fs = require('fs');
    const outputPath = path.join(__dirname, outputFile);
    if (fs.existsSync(outputPath)) {
        console.log(`WAV file created successfully: ${outputPath}`);
    } else {
        console.error("WAV file was not created.");
    }
});

