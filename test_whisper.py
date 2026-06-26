import whisper
import warnings
warnings.filterwarnings('ignore')
model = whisper.load_model('tiny')
result = model.transcribe('test_out.wav')
for segment in result['segments']:
    print(f"[{segment['start']:.2f} to {segment['end']:.2f}] {segment['text']}")
