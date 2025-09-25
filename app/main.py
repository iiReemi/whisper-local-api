from fastapi import FastAPI, UploadFile
from faster_whisper import WhisperModel
import tempfile, os

app = FastAPI()

# Modelo "small" (rápido). Pode usar "medium" ou "large-v3" se tiver GPU
model = WhisperModel("small", device="cpu")

@app.post("/transcribe")
async def transcribe(file: UploadFile):
    # Salvar temporário
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Transcrever
    segments, info = model.transcribe(
        tmp_path,
        language="pt",
        beam_size=5,              # melhora precisão
        best_of=5,                # tenta combinações
        vad_filter=True,          # ativa detecção de silêncio (corta mais frases)
        condition_on_previous_text=False,
        no_speech_threshold=0.6,  # controla corte em silêncio
        compression_ratio_threshold=2.4,
        log_prob_threshold=-1.0,
        initial_prompt=None,
        word_timestamps=False,
        # chunk_length = 30     # tamanho máximo de cada pedaço de áudio em segundos
    )


    MAX_WORDS = 4  # máx. de palavras por frase
    final_segments = []

    for seg in segments:
        words = seg.text.strip().split()
        current = []
        start_time = seg.start

        for w in words:
            current.append(w)
            if len(current) >= MAX_WORDS:
                final_segments.append({
                    "start": start_time,
                    "end": seg.end,  # poderia calcular mais exato se usar word_timestamps=True
                    "text": " ".join(current)
                })
                current = []
                start_time = seg.end

        if current:
            final_segments.append({
                "start": start_time,
                "end": seg.end,
                "text": " ".join(current)
            })

    os.remove(tmp_path)
    return {"segments": final_segments}
