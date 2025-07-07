import os
import sys
import whisper

def transcribe_audio(file_path):
    print(f"[+] 파일 로드 중: {file_path}")
    model = whisper.load_model("base")  # 'small', 'medium', 'large' 도 가능
    result = model.transcribe(file_path, language="ko")
    text = result["text"]

    out_path = os.path.splitext(file_path)[0] + "_transcription.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"[✔] 변환 완료! 결과 저장 위치: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: whisper_transcriber.exe <음성파일경로>")
        sys.exit(1)
    transcribe_audio(sys.argv[1])