# Avatar Engine — Полный пайплайн генерации аватаров на Python

> Документ охватывает все уровни: от SVG-аватара без зависимостей до фотореалистичного говорящего digital human с lip-sync, клонированием голоса и анимацией эмоций.

---

## Оглавление

1. [Карта подходов: от простого к сложному](#1-карта-подходов)
2. [Уровень 0 — SVG-аватары без нейросетей](#2-уровень-0--svg-аватары-без-нейросетей)
3. [Уровень 1 — Генерация портретов через Stable Diffusion](#3-уровень-1--генерация-портретов-через-stable-diffusion)
4. [Уровень 2 — Стилизация и Face Swap (InsightFace)](#4-уровень-2--стилизация-и-face-swap-insightface)
5. [Уровень 3 — Анализ лица: атрибуты и детекция (DeepFace)](#5-уровень-3--анализ-лица-атрибуты-и-детекция-deepface)
6. [Уровень 4 — Talking Avatar: фото → говорящее видео (SadTalker)](#6-уровень-4--talking-avatar-фото--говорящее-видео-sadtalker)
7. [Уровень 5 — Real-time Lip Sync (MuseTalk / Wav2Lip)](#7-уровень-5--real-time-lip-sync-musetalk--wav2lip)
8. [Уровень 6 — Клонирование голоса (XTTS / OpenVoice)](#8-уровень-6--клонирование-голоса-xtts--openvoice)
9. [Уровень 7 — Анимация эмоций и мимики (LivePortrait)](#9-уровень-7--анимация-эмоций-и-мимики-liveportrait)
10. [Уровень 8 — Полный Digital Human (ER-NeRF / GeneFace++)](#10-уровень-8--полный-digital-human-er-nerf--geneface)
11. [Постобработка и улучшение качества](#11-постобработка-и-улучшение-качества)
12. [Главный оркестратор пайплайна](#12-главный-оркестратор-пайплайна)
13. [Структура проекта и зависимости](#13-структура-проекта-и-зависимости)
14. [Этические ограничения и лицензии](#14-этические-ограничения-и-лицензии)

---

## 1. Карта подходов

Выбирай уровень в зависимости от задачи и железа:

| Уровень | Что получишь | GPU нужен? | Сложность | Время на кадр |
|---|---|---|---|---|
| **0** — SVG | Векторный мультяшный аватар | Нет | Минимальная | < 1 сек |
| **1** — SD Portrait | Фотореалистичный портрет по тексту | Желательно | Низкая | 5–30 сек |
| **2** — Face Swap | Перенос лица на сгенерированный портрет | Желательно | Низкая | 2–10 сек |
| **3** — DeepFace | Анализ атрибутов лица на фото | Нет (CPU) | Низкая | 0.5–2 сек |
| **4** — SadTalker | Фото → говорящее видео с движением головы | Да (4+ ГБ) | Средняя | RT × 3–5 |
| **5** — MuseTalk | Real-time lip-sync 30+ FPS | Да (GPU) | Средняя | Real-time |
| **6** — XTTS | Клонирование голоса по 6 сек аудио | Желательно | Средняя | < 5 сек |
| **7** — LivePortrait | Управление эмоциями и позой | Да (6+ ГБ) | Высокая | 1–3 сек/кадр |
| **8** — ER-NeRF | Полноценный NeRF digital human | Да (>16 ГБ) | Очень высокая | Часы на трейн |

**Рекомендуемый стек для вирусных Reels** (Уровни 1 + 2 + 4 + 6):
- Stable Diffusion → уникальный портрет аватара
- InsightFace → перенос нужного лица
- SadTalker → оживление с движением головы
- XTTS → клонированный или синтезированный голос

---

## 2. Уровень 0 — SVG-аватары без нейросетей

Быстрый старт. Работает везде, не требует GPU. Идеально для профильных иконок, placeholder-аватаров, User Generated Content.

### 2.1 Установка

```bash
pip install python-avatars cairosvg Pillow
```

### 2.2 Генерация SVG-аватара

```python
# svg_avatar.py
import python_avatars as pa
import random
from cairosvg import svg2png
from PIL import Image
import io

# Полностью случайный аватар
def generate_random_avatar(output_path: str = "output/avatar.png", size: int = 512):
    avatar = pa.Avatar.random()

    # Сохраняем SVG
    svg_path = output_path.replace(".png", ".svg")
    avatar.render(svg_path)

    # Конвертируем в PNG нужного размера
    svg2png(url=svg_path, write_to=output_path, output_width=size, output_height=size)
    print(f"  ✅ SVG-аватар: {output_path}")
    return output_path


# Аватар с заданными параметрами
def generate_custom_avatar(params: dict, output_path: str = "output/custom_avatar.png"):
    avatar = pa.Avatar(
        style=getattr(pa.AvatarStyle, params.get("style", "CIRCLE")),
        background_color=params.get("bg_color", pa.BackgroundColor.BLUE_01),
        top=getattr(pa.HairType, params.get("hair", "SHORT_FLAT")),
        hair_color=getattr(pa.HairColor, params.get("hair_color", "BLACK")),
        eyebrows=getattr(pa.EyebrowType, params.get("eyebrows", "DEFAULT")),
        eyes=getattr(pa.EyeType, params.get("eyes", "DEFAULT")),
        nose=getattr(pa.NoseType, params.get("nose", "DEFAULT")),
        mouth=getattr(pa.MouthType, params.get("mouth", "SMILE")),
        facial_hair=pa.FacialHairType.NONE,
        skin_color=params.get("skin_color", "#F8D5C2"),
        accessory=pa.AccessoryType.NONE,
        clothing=getattr(pa.ClothingType, params.get("clothing", "HOODIE")),
        clothing_color=getattr(pa.ClothingColor, params.get("clothing_color", "BLACK")),
    )

    svg_path = output_path.replace(".png", ".svg")
    avatar.render(svg_path)
    svg2png(url=svg_path, write_to=output_path, output_width=512, output_height=512)
    return output_path


# Батч-генерация уникальных аватаров
def generate_avatar_batch(count: int = 20, output_dir: str = "output/avatars") -> list[str]:
    import os
    os.makedirs(output_dir, exist_ok=True)

    paths = []
    for i in range(count):
        path = f"{output_dir}/avatar_{i:03d}.png"
        generate_random_avatar(path)
        paths.append(path)

    print(f"  ✅ Сгенерировано {count} аватаров")
    return paths
```

### 2.3 Доступные параметры `python-avatars`

| Параметр | Значения (примеры) |
|---|---|
| `AvatarStyle` | `CIRCLE`, `TRANSPARENT` |
| `HairType` | `SHORT_FLAT`, `STRAIGHT_1/2`, `CURLY`, `LONG_STRAIGHT`, `BUN`, `HIJAB`, `TURBAN`, `HAT`, `WINTER_HAT_1–4` |
| `HairColor` | `BLACK`, `BLONDE`, `BROWN`, `RED`, `GREY`, `PLATINUM`, `PASTEL_PINK` |
| `EyeType` | `DEFAULT`, `CLOSED`, `CRY`, `DIZZY`, `HAPPY`, `HEARTS`, `SIDE`, `WINK` |
| `MouthType` | `SMILE`, `SAD`, `SERIOUS`, `SCREAM_OPEN`, `EATING`, `TONGUE`, `VOMIT` |
| `ClothingType` | `HOODIE`, `SHIRT_CREW_NECK`, `BLAZER_SHIRT`, `GRAPHIC` |
| `SkinColor` | hex-строка: `"#F8D5C2"`, `"#B37A4C"`, `"#614335"` |

---

## 3. Уровень 1 — Генерация портретов через Stable Diffusion

Создаём фотореалистичный или стилизованный портрет аватара по текстовому промпту. Без исходного фото.

### 3.1 Установка

```bash
# Локальный запуск через diffusers
pip install diffusers transformers accelerate torch torchvision
pip install xformers  # опционально, ускоряет на Nvidia

# Или запуск через API (без GPU)
pip install replicate  # Replicate API
pip install stability-sdk  # Stability AI API
```

### 3.2 Локальная генерация (SDXL)

```python
# portrait_generator.py
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import random

# Загружаем однократно
_pipe = None

def get_pipeline(model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"):
    global _pipe
    if _pipe is None:
        _pipe = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            use_safetensors=True,
        )
        _pipe.scheduler = DPMSolverMultistepScheduler.from_config(_pipe.scheduler.config)
        _pipe = _pipe.to("cuda")
        _pipe.enable_xformers_memory_efficient_attention()  # если установлен xformers
    return _pipe


# Шаблоны промптов для аватаров
AVATAR_PROMPTS = {
    "realistic_woman": (
        "portrait photo of a young woman, professional headshot, "
        "studio lighting, sharp focus, 8k uhd, high quality",
        "ugly, deformed, blurry, watermark, text, bad anatomy"
    ),
    "realistic_man": (
        "portrait photo of a professional man, confident look, "
        "studio lighting, photorealistic, sharp features, 8k",
        "ugly, deformed, blurry, watermark, cartoon"
    ),
    "anime_girl": (
        "anime portrait of a girl, detailed eyes, colorful hair, "
        "high quality anime art style, studio ghibli inspired",
        "realistic, 3d, ugly, deformed"
    ),
    "cyberpunk": (
        "cyberpunk character portrait, neon lighting, futuristic, "
        "sci-fi aesthetic, ultra detailed, cinematic",
        "blurry, ugly, watermark"
    ),
    "fantasy_warrior": (
        "fantasy warrior portrait, epic armor, dramatic lighting, "
        "concept art, highly detailed, oil painting style",
        "blurry, watermark, ugly"
    ),
    "vtuber": (
        "2d anime vtuber avatar, cute character design, "
        "colorful, expressive, clean lineart, white background",
        "realistic, 3d, ugly"
    ),
}


def generate_portrait(
    style: str = "realistic_woman",
    custom_prompt: str = None,
    output_path: str = "output/portrait.png",
    width: int = 1024,
    height: int = 1024,
    steps: int = 30,
    cfg_scale: float = 7.5,
    seed: int = None
) -> str:
    pipe = get_pipeline()

    if custom_prompt:
        positive, negative = custom_prompt, "ugly, blurry, watermark"
    else:
        positive, negative = AVATAR_PROMPTS.get(style, AVATAR_PROMPTS["realistic_woman"])

    generator = torch.Generator("cuda")
    if seed is None:
        seed = random.randint(0, 2**32 - 1)
    generator.manual_seed(seed)

    result = pipe(
        prompt=positive,
        negative_prompt=negative,
        width=width,
        height=height,
        num_inference_steps=steps,
        guidance_scale=cfg_scale,
        generator=generator,
    )

    image = result.images[0]
    image.save(output_path)
    print(f"  ✅ Портрет сгенерирован (seed={seed}): {output_path}")
    return output_path


# Батч-генерация разных стилей
def generate_style_variants(base_prompt: str, n_variants: int = 4) -> list[str]:
    styles = ["realistic_woman", "anime_girl", "cyberpunk", "fantasy_warrior"]
    paths = []
    for i, style in enumerate(styles[:n_variants]):
        path = f"output/variant_{style}.png"
        generate_portrait(style=style, output_path=path)
        paths.append(path)
    return paths
```

### 3.3 Через Replicate API (без GPU)

```python
# portrait_via_api.py
import replicate
import requests
from pathlib import Path

# В .env: REPLICATE_API_TOKEN=r8_...

def generate_portrait_api(
    prompt: str,
    output_path: str = "output/portrait_api.png",
    model: str = "stability-ai/sdxl"
) -> str:
    output = replicate.run(
        f"{model}:latest",
        input={
            "prompt": prompt,
            "negative_prompt": "ugly, deformed, blurry, watermark",
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 30,
        }
    )

    # Скачиваем результат
    image_url = output[0]
    response = requests.get(image_url)
    Path(output_path).write_bytes(response.content)
    return output_path
```

---

## 4. Уровень 2 — Стилизация и Face Swap (InsightFace)

Переносим конкретное лицо (из фото пользователя) на сгенерированный портрет. Сохраняется идентичность человека, меняется стиль/фон/одежда.

### 4.1 Установка

```bash
# InsightFace — MIT лицензия (код), модели только non-commercial
pip install insightface onnxruntime-gpu  # или onnxruntime для CPU
pip install opencv-python Pillow numpy

# Скачиваем модель (однократно)
# inswapper_128.onnx — скачать с HuggingFace:
# https://huggingface.co/deepinsight/inswapper/resolve/main/inswapper_128.onnx
# Положить в: models/insightface/inswapper_128.onnx
```

```bash
# buffalo_l — автоскачивается при первом запуске insightface
# или вручную: ~/.insightface/models/buffalo_l/
```

### 4.2 Face Swap

```python
# face_swap.py
import insightface
from insightface.app import FaceAnalysis
import cv2
import numpy as np
from PIL import Image

# Инициализируем однократно
_app = None
_swapper = None

def get_face_tools():
    global _app, _swapper
    if _app is None:
        _app = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
        _app.prepare(ctx_id=0, det_size=(640, 640))
    if _swapper is None:
        import onnxruntime
        _swapper = insightface.model_zoo.get_model(
            "models/insightface/inswapper_128.onnx",
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )
    return _app, _swapper


def swap_face(
    source_image_path: str,   # фото с нужным лицом (пользователь)
    target_image_path: str,   # сгенерированный портрет
    output_path: str = "output/swapped.png"
) -> str:
    app, swapper = get_face_tools()

    # Загружаем изображения
    source = cv2.imread(source_image_path)
    target = cv2.imread(target_image_path)

    # Детектируем лица
    source_faces = app.get(source)
    target_faces = app.get(target)

    if not source_faces:
        raise ValueError(f"Лицо не найдено на изображении-источнике: {source_image_path}")
    if not target_faces:
        raise ValueError(f"Лицо не найдено на целевом изображении: {target_image_path}")

    # Берём первое лицо из каждого изображения
    source_face = sorted(source_faces, key=lambda x: x.bbox[2] - x.bbox[0], reverse=True)[0]

    result = target.copy()
    for target_face in target_faces:
        result = swapper.get(result, target_face, source_face, paste_back=True)

    cv2.imwrite(output_path, result)
    print(f"  ✅ Face swap: {output_path}")
    return output_path


def extract_face_embedding(image_path: str) -> np.ndarray:
    """Извлекает embedding лица для дальнейшего использования."""
    app, _ = get_face_tools()
    img = cv2.imread(image_path)
    faces = app.get(img)
    if not faces:
        raise ValueError("Лицо не найдено")
    return faces[0].normed_embedding  # 512-мерный вектор


def enhance_face(image_path: str, output_path: str = None) -> str:
    """
    Улучшение качества лица через GFPGAN / CodeFormer.
    Устанавливай: pip install gfpgan
    """
    from gfpgan import GFPGANer

    if output_path is None:
        output_path = image_path.replace(".png", "_enhanced.png")

    restorer = GFPGANer(
        model_path="models/GFPGANv1.4.pth",
        upscale=2,
        arch="clean",
        channel_multiplier=2,
    )

    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    _, _, restored_img = restorer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)

    cv2.imwrite(output_path, restored_img)
    return output_path
```

### 4.3 InstantID — сохранение идентичности при SD-генерации

Более качественный способ: встраиваем embedding лица прямо в диффузию.

```python
# instant_id.py
"""
InstantID позволяет генерировать новые стилизованные портреты,
сохраняя идентичность конкретного человека.

Установка:
pip install diffusers transformers accelerate insightface
Модели: https://huggingface.co/InstantX/InstantID
"""
from diffusers import StableDiffusionXLPipeline
from diffusers.utils import load_image
import torch
from insightface.app import FaceAnalysis

def generate_with_instant_id(
    reference_photo: str,          # фото нужного человека
    prompt: str,
    output_path: str = "output/instant_id.png",
    style: str = "photorealistic"
) -> str:
    from pipeline_stable_diffusion_xl_instantid import StableDiffusionXLInstantIDPipeline

    # Инициализация
    app = FaceAnalysis(name="antelopev2", root="models/")
    app.prepare(ctx_id=0, det_size=(640, 640))

    # Извлекаем embedding лица
    image = load_image(reference_photo)
    faces = app.get(np.array(image))
    face_emb = faces[0].normed_embedding
    face_kps = draw_kps(image, faces[0].kps)  # keypoints для ControlNet

    # Генерируем
    pipe = StableDiffusionXLInstantIDPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16
    ).to("cuda")

    pipe.load_ip_adapter_instantid("models/InstantID/ip-adapter.bin")
    pipe.load_controlnet_instantid("models/InstantID/ControlNetModel")

    result = pipe(
        prompt=prompt,
        image_embeds=face_emb,
        image=face_kps,
        controlnet_conditioning_scale=0.8,
        ip_adapter_scale=0.8,
    ).images[0]

    result.save(output_path)
    return output_path
```

---

## 5. Уровень 3 — Анализ лица: атрибуты и детекция (DeepFace)

Нужен для адаптации аватара под конкретного пользователя: определяем возраст, пол, эмоцию — и подбираем подходящий стиль аватара.

### 5.1 Установка

```bash
pip install deepface  # MIT лицензия
# Модели скачиваются автоматически при первом вызове
```

### 5.2 Анализ и адаптация аватара

```python
# face_analyzer.py
from deepface import DeepFace
import json

def analyze_user_photo(image_path: str) -> dict:
    """
    Анализирует фото пользователя и возвращает атрибуты
    для подбора стиля аватара.
    """
    result = DeepFace.analyze(
        img_path=image_path,
        actions=["age", "gender", "emotion", "race"],
        enforce_detection=True,
        detector_backend="retinaface",  # retinaface лучший по точности
    )

    # Берём первое лицо
    face_data = result[0] if isinstance(result, list) else result

    return {
        "age": face_data["age"],
        "gender": face_data["dominant_gender"],
        "emotion": face_data["dominant_emotion"],
        "ethnicity": face_data["dominant_race"],
        "emotion_scores": face_data["emotion"],
    }


def recommend_avatar_style(face_data: dict) -> dict:
    """На основе анализа лица рекомендует стиль аватара."""
    age = face_data["age"]
    gender = face_data["gender"].lower()
    emotion = face_data["emotion"]

    # Логика подбора стиля
    if age < 25:
        if emotion in ["happy", "surprise"]:
            style = "anime_girl" if gender == "woman" else "anime"
            prompt_hint = "young, energetic, colorful"
        else:
            style = "cyberpunk"
            prompt_hint = "edgy, stylish, futuristic"
    elif age < 40:
        style = "realistic_woman" if gender == "woman" else "realistic_man"
        prompt_hint = "professional, confident, studio lighting"
    else:
        style = "fantasy_warrior" if emotion in ["angry", "neutral"] else "realistic_man"
        prompt_hint = "mature, distinguished, strong"

    return {
        "recommended_style": style,
        "prompt_additions": prompt_hint,
        "face_data": face_data,
    }


def verify_same_person(image1: str, image2: str) -> dict:
    """Проверяет, одно ли лицо на двух фото."""
    result = DeepFace.verify(
        img1_path=image1,
        img2_path=image2,
        model_name="ArcFace",
        detector_backend="retinaface",
    )
    return {
        "same_person": result["verified"],
        "distance": result["distance"],
        "threshold": result["threshold"],
        "confidence": 1 - result["distance"] / result["threshold"]
    }
```

---

## 6. Уровень 4 — Talking Avatar: фото → говорящее видео (SadTalker)

Фотопортрет + аудиофайл = видео с движением головы, синхронизацией губ и выражением лица. SadTalker использует 3D Morphable Model — поэтому движения выглядят натурально.

### 6.1 Установка

```bash
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker

conda create -n sadtalker python=3.9
conda activate sadtalker

pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# Скачиваем веса (скрипт из репо)
bash scripts/download_models.sh

# Или вручную с HuggingFace:
# https://huggingface.co/vinthony/SadTalker
```

**Минимальные требования:** GPU 4 ГБ VRAM, CUDA 11.8+

### 6.2 Запуск через Python API

```python
# sadtalker_wrapper.py
import subprocess
import os
import sys

SADTALKER_PATH = "external/SadTalker"  # путь к клонированному репо

def generate_talking_avatar(
    portrait_path: str,           # .jpg/.png портрет
    audio_path: str,              # .wav/.mp3 речь
    output_dir: str = "output",
    preprocess: str = "crop",     # crop | resize | full | extcrop | extfull
    still_mode: bool = False,     # минимальное движение головы (ближе к живому)
    expression_scale: float = 1.0, # 0.0 = нейтральный, 2.0 = гиперэкспрессивный
    enhancer: str = "gfpgan",     # gfpgan | RestoreFormer | None
    pose_style: int = 0,          # 0–45, стиль движения головы
    size: int = 256,              # 256 или 512 (требует больше памяти)
) -> str:
    """
    Запускает SadTalker и возвращает путь к видео.
    """
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        sys.executable,
        os.path.join(SADTALKER_PATH, "inference.py"),
        "--driven_audio", audio_path,
        "--source_image", portrait_path,
        "--result_dir", output_dir,
        "--preprocess", preprocess,
        "--expression_scale", str(expression_scale),
        "--pose_style", str(pose_style),
        "--size", str(size),
    ]

    if still_mode:
        cmd.append("--still")

    if enhancer and enhancer != "None":
        cmd.extend(["--enhancer", enhancer])

    # Запускаем в рабочей директории SadTalker
    result = subprocess.run(
        cmd,
        cwd=SADTALKER_PATH,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"SadTalker ошибка:\n{result.stderr}")

    # Находим созданное видео
    created_files = []
    for f in os.listdir(output_dir):
        if f.endswith(".mp4"):
            created_files.append(os.path.join(output_dir, f))

    if not created_files:
        raise RuntimeError("SadTalker не создал видео файл")

    latest = max(created_files, key=os.path.getctime)
    print(f"  ✅ Talking avatar: {latest}")
    return latest


def batch_expressions(
    portrait_path: str,
    audio_path: str,
    expression_scales: list = [0.5, 1.0, 1.5, 2.0],
    output_dir: str = "output/expressions"
) -> list[str]:
    """Генерирует варианты с разной степенью эмоциональности."""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for scale in expression_scales:
        out = os.path.join(output_dir, f"expr_{scale}.mp4")
        path = generate_talking_avatar(portrait_path, audio_path, output_dir, expression_scale=scale)
        results.append(path)
    return results
```

### 6.3 Управление стилем движений

```python
# Параметры pose_style (0–45) задают паттерн движения головы
POSE_STYLES = {
    "neutral":     0,   # минимальное движение
    "nodding":     5,   # кивание
    "looking_up": 15,   # взгляд вверх
    "tilted":     25,   # наклон головы
    "active":     35,   # активное движение
    "dynamic":    45,   # максимальная динамика
}

# Режимы предобработки
PREPROCESS_MODES = {
    "crop":    "Вырезает и масштабирует лицо — рекомендуется для портретов",
    "resize":  "Просто масштабирует всё изображение",
    "full":    "Анимирует на полном кадре — для поясных снимков",
    "extcrop": "Расширенный crop — больше контекста вокруг лица",
    "extfull": "Полный кадр с расширенной областью",
}
```

---

## 7. Уровень 5 — Real-time Lip Sync (MuseTalk / Wav2Lip)

Если у тебя уже есть видео с человеком — меняем только губы под новое аудио. Real-time 30+ FPS с GPU.

### 7.1 Wav2Lip — быстро и надёжно

```bash
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip
pip install -r requirements.txt

# Скачать веса: https://github.com/Rudrabha/Wav2Lip#getting-the-weights
# Положить в Wav2Lip/checkpoints/wav2lip_gan.pth
```

```python
# wav2lip_wrapper.py
import subprocess, os, sys

WAV2LIP_PATH = "external/Wav2Lip"

def apply_lipsync(
    video_path: str,          # видео с лицом (или фото — тогда будет 1-frame loop)
    audio_path: str,          # новое аудио
    output_path: str = "output/lipsync.mp4",
    use_hd_model: bool = True,  # gan-модель — лучше качество
    pads: tuple = (0, 10, 0, 0),  # отступы от лица (top, bottom, left, right)
) -> str:

    checkpoint = "wav2lip_gan.pth" if use_hd_model else "wav2lip.pth"

    cmd = [
        sys.executable,
        os.path.join(WAV2LIP_PATH, "inference.py"),
        "--checkpoint_path", os.path.join(WAV2LIP_PATH, "checkpoints", checkpoint),
        "--face", video_path,
        "--audio", audio_path,
        "--outfile", output_path,
        "--pads", *[str(p) for p in pads],
    ]

    result = subprocess.run(cmd, cwd=WAV2LIP_PATH, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Wav2Lip ошибка:\n{result.stderr}")

    print(f"  ✅ Lip sync: {output_path}")
    return output_path
```

### 7.2 MuseTalk — высокое качество, real-time

```bash
git clone https://github.com/TMElyralab/MuseTalk.git
cd MuseTalk
pip install -r requirements.txt

# Скачать модели (HuggingFace):
# https://huggingface.co/TMElyralab/MuseTalk
```

```python
# musetalk_wrapper.py
import subprocess, os, json

MUSETALK_PATH = "external/MuseTalk"

def musetalk_inference(
    avatar_path: str,       # исходное фото или видео аватара
    audio_path: str,        # аудио для синхронизации
    output_path: str = "output/musetalk_result.mp4",
    bbox_shift: int = 0,    # смещение бокса лица
) -> str:
    """
    MuseTalk — диффузионная модель lip-sync, 256×256 лицо.
    Значительно лучше Wav2Lip по реализму, особенно крупные планы.
    """
    config = {
        "avatar_path": avatar_path,
        "audio_path": audio_path,
        "output_path": output_path,
        "bbox_shift": bbox_shift,
        "fps": 25,
    }

    config_file = "temp/musetalk_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    cmd = [
        "python", os.path.join(MUSETALK_PATH, "inference.py"),
        "--config", config_file
    ]

    result = subprocess.run(cmd, cwd=MUSETALK_PATH, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"MuseTalk ошибка:\n{result.stderr}")

    return output_path


# Сравнение MuseTalk vs Wav2Lip
LIPSYNC_COMPARISON = """
| Критерий          | Wav2Lip       | MuseTalk          |
|---|---|---|
| Архитектура       | GAN           | Latent Diffusion  |
| Скорость          | ~60 FPS       | 30+ FPS (GPU)     |
| Качество губ      | Хорошее       | Отличное          |
| Движение головы   | Нет           | Нет               |
| Разрешение лица   | 96px          | 256px             |
| Real-time         | Да            | Да (с GPU)        |
| Лицензия          | Только research | MIT              |
"""
```

---

## 8. Уровень 6 — Клонирование голоса (XTTS / OpenVoice)

Аватар должен говорить именно своим голосом. 6 секунд референсного аудио достаточно.

### 8.1 XTTS v2 (Coqui) — многоязычный

```bash
pip install TTS  # Coqui TTS, включает XTTS v2
```

```python
# voice_cloner.py
from TTS.api import TTS
import torch

_tts = None

def get_tts():
    global _tts
    if _tts is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    return _tts


def clone_voice_and_speak(
    text: str,
    reference_audio: str,   # 6+ секунд чистой речи референса
    output_path: str = "output/cloned_speech.wav",
    language: str = "ru"    # ru, en, de, fr, es, ...
) -> str:
    """
    Синтезирует текст голосом из reference_audio.
    Минимальная длина референса: 6 секунд. Оптимально: 15–30 сек.
    """
    tts = get_tts()

    tts.tts_to_file(
        text=text,
        speaker_wav=reference_audio,
        language=language,
        file_path=output_path,
    )

    print(f"  ✅ Клонированный голос: {output_path}")
    return output_path


# XTTS с управлением эмоциями через описание
XTTS_EMOTION_HINTS = {
    "excited":    "говори с воодушевлением и энергично",
    "sad":        "говори тихо и грустно",
    "professional": "говори чётко и профессионально",
    "friendly":   "говори тепло и дружелюбно",
}

def speak_with_emotion(text: str, reference_audio: str, emotion: str = "friendly") -> str:
    hint = XTTS_EMOTION_HINTS.get(emotion, "")
    # XTTS не поддерживает прямое управление эмоциями через промпт,
    # но можно влиять через знаки препинания и паузы
    if emotion == "excited":
        text = text.replace(".", "!").replace(",", "!")
    elif emotion == "sad":
        text = "... " + text.replace(".", "...").replace(",", "...")

    return clone_voice_and_speak(text, reference_audio)
```

### 8.2 OpenVoice v2 — контроль стиля голоса

```bash
pip install openvoice
# Модели: https://huggingface.co/myshell-ai/OpenVoice
```

```python
# openvoice_wrapper.py
"""
OpenVoice v2: клонирование голоса + управление:
- тоном (тихий/громкий)
- скоростью речи
- акцентом
"""
from openvoice import se_extractor
from openvoice.api import ToneColorConverter

def clone_with_style_control(
    text: str,
    reference_audio: str,
    output_path: str = "output/openvoice.wav",
    speed: float = 1.0,       # 0.5 = медленно, 1.5 = быстро
    target_language: str = "EN"
) -> str:
    converter = ToneColorConverter("models/openvoice/converter/checkpoint.pth")
    converter.load_ckpt("models/openvoice/converter/config.json")

    # Извлекаем тембр голоса
    source_se, _ = se_extractor.get_se(reference_audio, converter, vad=True)

    # Генерируем базовую речь (MeloTTS) с нужной скоростью
    from melo.api import TTS
    model = TTS(language=target_language, device="auto")
    speaker_id = model.hps.data.spk2id[target_language]
    base_audio = "temp/base_speech.wav"
    model.tts_to_file(text, speaker_id, base_audio, speed=speed)

    # Применяем тембр референса
    target_se, _ = se_extractor.get_se(base_audio, converter, vad=True)

    converter.convert(
        audio_src_path=base_audio,
        src_se=target_se,
        tgt_se=source_se,
        output_path=output_path,
    )

    return output_path
```

---

## 9. Уровень 7 — Анимация эмоций и мимики (LivePortrait)

LivePortrait — управление позой головы, направлением взгляда, выражением лица через контрольные точки или другое видео-референс.

### 9.1 Установка

```bash
git clone https://github.com/KwaiVGI/LivePortrait.git
cd LivePortrait
pip install -r requirements.txt

# Скачать веса:
# https://huggingface.co/KwaiVGI/LivePortrait
# Положить в LivePortrait/pretrained_weights/
```

**Требования:** GPU 6+ ГБ VRAM (рекомендуется 8+ ГБ)

### 9.2 Анимация по видео-референсу

```python
# liveportrait_wrapper.py
import subprocess, os

LIVEPORTRAIT_PATH = "external/LivePortrait"

def animate_portrait(
    source_portrait: str,    # статичный портрет (фото)
    driving_video: str,      # видео с движениями для копирования
    output_path: str = "output/animated.mp4",
    flag_crop_driving_video: bool = True,
    animation_region: str = "all",  # all | eyes | mouth | pose | expression
) -> str:
    """
    Анимирует статичный портрет, копируя движения из driving_video.
    Оригинальная идентичность сохраняется (не face swap).
    """
    cmd = [
        "python", os.path.join(LIVEPORTRAIT_PATH, "inference.py"),
        "-s", source_portrait,
        "-d", driving_video,
        "-o", os.path.dirname(output_path),
        "--output_name", os.path.basename(output_path).replace(".mp4", ""),
        "--animation_region", animation_region,
    ]

    if flag_crop_driving_video:
        cmd.append("--flag_crop_driving_video")

    result = subprocess.run(cmd, cwd=LIVEPORTRAIT_PATH, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"LivePortrait ошибка:\n{result.stderr}")

    return output_path


def animate_expression_only(source: str, driving: str, output: str) -> str:
    """Переносим только выражение лица (без позы)."""
    return animate_portrait(source, driving, output, animation_region="expression")


def animate_eyes_only(source: str, driving: str, output: str) -> str:
    """Только моргание и движение глаз — для idle-анимации аватара."""
    return animate_portrait(source, driving, output, animation_region="eyes")


# Создание idle-анимации (мигание/дыхание) без driving video
def create_idle_animation(portrait: str, output: str = "output/idle.mp4", duration: int = 5) -> str:
    """
    Генерирует петлевую idle-анимацию: мигание, лёгкое покачивание головы.
    Используется как фон между речевыми репликами.
    """
    # Используем синтетическое driving видео из встроенных шаблонов LivePortrait
    template_dir = os.path.join(LIVEPORTRAIT_PATH, "assets/examples/driving")
    idle_template = os.path.join(template_dir, "d14.mp4")  # шаблон мигания

    return animate_portrait(portrait, idle_template, output, animation_region="eyes")
```

---

## 10. Уровень 8 — Полный Digital Human (ER-NeRF / GeneFace++)

Тренируем персонализированную нейросеть на конкретном человеке. Результат: видео-синтез в реальном времени с его точной мимикой.

### 10.1 ER-NeRF — Real-time NeRF для digital human

```bash
git clone https://github.com/Fictionarry/ER-NeRF.git
cd ER-NeRF
pip install -r requirements.txt

# Требования: GPU 16+ ГБ VRAM, CUDA 11.8+
# Время обучения: 1–2 часа на RTX 3090
```

```python
# er_nerf_pipeline.py
"""
ER-NeRF пайплайн:
1. Подготовка данных (видео → кадры → кропы лица → 3D-параметры)
2. Обучение модели на конкретном человеке (~60 мин)
3. Инференс: аудио → видео real-time

Подходит для:
- Фиксированного персонажа (блогер, персонаж бренда)
- Высокого качества (точная мимика, кожа, освещение)
- Когда аватар будет использоваться много раз
"""
import subprocess, os

ERNERF_PATH = "external/ER-NeRF"

def prepare_data(video_path: str, person_id: str = "avatar") -> str:
    """
    Шаг 1: Извлечение и разметка данных из видео.
    Видео: 3–5 минут, лицо фронтально, равномерное освещение.
    """
    output_dir = f"data/er_nerf/{person_id}"
    os.makedirs(output_dir, exist_ok=True)

    subprocess.run([
        "python", os.path.join(ERNERF_PATH, "data_utils/process.py"),
        video_path, "--id", person_id, "--out", output_dir
    ], check=True)

    return output_dir


def train_nerf(person_id: str, data_dir: str, epochs: int = 200) -> str:
    """
    Шаг 2: Обучение NeRF-модели.
    """
    model_dir = f"models/er_nerf/{person_id}"

    subprocess.run([
        "python", os.path.join(ERNERF_PATH, "main.py"),
        "--path", data_dir,
        "--workspace", model_dir,
        "--iters", str(epochs * 1000),
        "--train",
    ], check=True, cwd=ERNERF_PATH)

    return model_dir


def synthesize_video(audio_path: str, person_id: str, output_path: str = "output/nerf_result.mp4") -> str:
    """
    Шаг 3: Синтез видео из аудио.
    """
    model_dir = f"models/er_nerf/{person_id}"
    data_dir = f"data/er_nerf/{person_id}"

    subprocess.run([
        "python", os.path.join(ERNERF_PATH, "main.py"),
        "--path", data_dir,
        "--workspace", model_dir,
        "--test",
        "--test_train",
        "--asr_model", "hubert",
        "--aud", audio_path,
        "--save_video", output_path,
    ], check=True, cwd=ERNERF_PATH)

    return output_path
```

### 10.2 GeneFace++ — более высокое качество

```bash
git clone https://github.com/yerlan2/GeneFacePlusPlus.git
# Подробная инструкция: https://genefaceplusplus.github.io
# Требования: GPU 24+ ГБ для обучения (A100 / RTX 4090)
```

**Когда использовать ER-NeRF vs GeneFace++:**

| Критерий | ER-NeRF | GeneFace++ |
|---|---|---|
| Качество | Хорошее | Отличное |
| VRAM для обучения | 16 ГБ | 24+ ГБ |
| Время обучения | ~1 час | ~4 часа |
| Real-time | Да | Нет (post-process) |
| Движение головы | Ограниченное | Выраженное |
| Лицензия | MIT | Только research |

---

## 11. Постобработка и улучшение качества

```python
# postprocessing.py
import cv2
import numpy as np
import subprocess
from PIL import Image

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GFPGAN — улучшение лица до 8x
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def enhance_face_gfpgan(input_path: str, output_path: str = None, upscale: int = 2) -> str:
    """
    Убирает артефакты, восстанавливает детали лица.
    Установка: pip install gfpgan
    Модель: https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth
    """
    from gfpgan import GFPGANer

    output_path = output_path or input_path.replace(".png", "_hd.png")

    restorer = GFPGANer(
        model_path="models/GFPGANv1.4.pth",
        upscale=upscale,
        arch="clean",
        channel_multiplier=2,
    )

    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    _, _, restored = restorer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
    cv2.imwrite(output_path, restored)
    return output_path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CodeFormer — ещё более качественное восстановление
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def enhance_face_codeformer(input_path: str, output_path: str = None, fidelity: float = 0.7) -> str:
    """
    fidelity: 0.0 = максимальное улучшение (может изменить лицо)
              1.0 = максимальная верность оригиналу
    Оптимально: 0.5–0.7

    Установка: pip install basicsr facexlib
    git clone https://github.com/sczhou/CodeFormer.git
    """
    output_path = output_path or input_path.replace(".png", "_cf.png")

    subprocess.run([
        "python", "external/CodeFormer/inference_codeformer.py",
        "-w", str(fidelity),
        "--input_path", input_path,
        "--output_path", output_path,
        "--face_upsample",
    ], check=True)

    return output_path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Удаление фона (для аватаров без фона)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def remove_background(input_path: str, output_path: str = None) -> str:
    """
    Удаляет фон, сохраняет прозрачность (PNG с alpha).
    Установка: pip install rembg
    """
    from rembg import remove
    from PIL import Image
    import io

    output_path = output_path or input_path.replace(".jpg", "_nobg.png").replace(".jpeg", "_nobg.png")

    with open(input_path, "rb") as f:
        input_data = f.read()

    output_data = remove(input_data)

    with open(output_path, "wb") as f:
        f.write(output_data)

    return output_path


def add_custom_background(portrait_path: str, background_path: str, output_path: str) -> str:
    """Накладывает аватар без фона на кастомный бэкграунд."""
    avatar = Image.open(portrait_path).convert("RGBA")
    background = Image.open(background_path).convert("RGBA")
    background = background.resize(avatar.size)

    combined = Image.alpha_composite(background, avatar)
    combined.save(output_path)
    return output_path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RealESRGAN — апскейл видео / изображений
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def upscale_image(input_path: str, output_path: str = None, scale: int = 4) -> str:
    """
    Увеличивает разрешение в 2x или 4x с сохранением деталей.
    pip install realesrgan basicsr
    """
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
    import torch

    output_path = output_path or input_path.replace(".png", f"_{scale}x.png")

    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale)
    upsampler = RealESRGANer(
        scale=scale,
        model_path=f"models/RealESRGAN_x{scale}plus.pth",
        model=model,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )

    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    output, _ = upsampler.enhance(img, outscale=scale)
    cv2.imwrite(output_path, output)
    return output_path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Постобработка видео через ffmpeg
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def postprocess_video(
    input_video: str,
    output_video: str,
    add_lut: str = None,          # путь к .cube LUT
    denoise: bool = True,          # шумоподавление
    sharpen: bool = True,          # резкость
    brightness: float = 1.05,
    saturation: float = 1.1,
) -> str:
    vf_parts = []

    if denoise:
        vf_parts.append("hqdn3d=1.5:1.5:6:6")

    if sharpen:
        vf_parts.append("unsharp=3:3:0.5:3:3:0.0")

    vf_parts.append(f"eq=brightness={brightness - 1:.2f}:saturation={saturation:.2f}")

    if add_lut:
        vf_parts.append(f"lut3d={add_lut}")

    vf_chain = ",".join(vf_parts)

    subprocess.run([
        "ffmpeg", "-y", "-i", input_video,
        "-vf", vf_chain,
        "-c:v", "libx264", "-crf", "18",
        "-c:a", "copy",
        output_video
    ], check=True)

    return output_video
```

---

## 12. Главный оркестратор пайплайна

```python
# avatar_engine.py
"""
Полный пайплайн создания говорящего аватара:
Фото пользователя + текст → стилизованный говорящий аватар
"""
import os
from datetime import datetime

from svg_avatar import generate_random_avatar
from portrait_generator import generate_portrait
from face_swap import swap_face, enhance_face
from face_analyzer import analyze_user_photo, recommend_avatar_style
from voice_cloner import clone_voice_and_speak
from sadtalker_wrapper import generate_talking_avatar
from postprocessing import remove_background, postprocess_video


def create_avatar_pipeline(
    # Входные данные
    user_photo: str = None,      # фото пользователя (опционально)
    reference_voice: str = None, # аудио для клонирования голоса (опционально)
    script_text: str = "Привет! Я твой новый аватар.",

    # Стиль
    avatar_style: str = "auto",  # auto | realistic | anime | cyberpunk | fantasy
    portrait_prompt: str = None, # кастомный промпт для SD

    # Параметры talking avatar
    expression_scale: float = 1.0,
    pose_style: int = 0,

    # Постобработка
    enhance: bool = True,
    remove_bg: bool = False,

    output_dir: str = "output",
) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {}

    # ── Шаг 1: Анализ фото пользователя (если есть) ──
    if user_photo and os.path.exists(user_photo):
        print("🔍 Анализируем фото пользователя...")
        face_data = analyze_user_photo(user_photo)
        recommendation = recommend_avatar_style(face_data)

        if avatar_style == "auto":
            avatar_style = recommendation["recommended_style"]
            print(f"   Рекомендованный стиль: {avatar_style}")

        results["face_analysis"] = face_data

    # ── Шаг 2: Генерация базового портрета ──
    print(f"🎨 Генерируем портрет в стиле '{avatar_style}'...")
    portrait_path = f"{output_dir}/portrait_{timestamp}.png"

    if portrait_prompt:
        generate_portrait(custom_prompt=portrait_prompt, output_path=portrait_path)
    else:
        generate_portrait(style=avatar_style, output_path=portrait_path)

    results["portrait"] = portrait_path

    # ── Шаг 3: Face swap (если есть фото пользователя) ──
    if user_photo and os.path.exists(user_photo):
        print("🔄 Переносим лицо пользователя на аватар...")
        swapped_path = f"{output_dir}/swapped_{timestamp}.png"
        swap_face(user_photo, portrait_path, swapped_path)
        portrait_path = swapped_path
        results["swapped"] = swapped_path

    # ── Шаг 4: Улучшение качества лица ──
    if enhance:
        print("✨ Улучшаем качество изображения...")
        enhanced_path = f"{output_dir}/enhanced_{timestamp}.png"
        enhance_face(portrait_path, enhanced_path)
        portrait_path = enhanced_path
        results["enhanced"] = enhanced_path

    # ── Шаг 5: Удаление фона (опционально) ──
    if remove_bg:
        print("🪄 Удаляем фон...")
        nobg_path = f"{output_dir}/nobg_{timestamp}.png"
        remove_background(portrait_path, nobg_path)
        results["no_background"] = nobg_path

    # ── Шаг 6: Синтез речи ──
    print("🎙 Синтезируем речь...")
    audio_path = f"temp/speech_{timestamp}.wav"

    if reference_voice and os.path.exists(reference_voice):
        clone_voice_and_speak(script_text, reference_voice, audio_path)
    else:
        # Используем edge-tts как fallback
        import asyncio, edge_tts
        async def _tts():
            comm = edge_tts.Communicate(script_text, "ru-RU-SvetlanaNeural")
            await comm.save(audio_path)
        asyncio.run(_tts())

    results["audio"] = audio_path

    # ── Шаг 7: Генерация talking avatar ──
    print("🎬 Создаём говорящий аватар...")
    raw_video_path = f"temp/raw_avatar_{timestamp}.mp4"

    generate_talking_avatar(
        portrait_path=portrait_path,
        audio_path=audio_path,
        output_dir="temp",
        expression_scale=expression_scale,
        pose_style=pose_style,
        enhancer=None,  # уже улучшили выше
    )

    # ── Шаг 8: Постобработка видео ──
    print("🎞 Постобработка видео...")
    final_path = f"{output_dir}/avatar_{timestamp}.mp4"
    postprocess_video(raw_video_path, final_path)

    results["final_video"] = final_path

    # Чистим temp
    for f in [audio_path, raw_video_path]:
        if os.path.exists(f):
            os.remove(f)

    size_mb = os.path.getsize(final_path) / 1024 / 1024
    print(f"\n✅ Аватар готов: {final_path} ({size_mb:.1f} МБ)")

    return results


# ────────────────────────────────────────
# Быстрый вариант: только SVG (без GPU)
# ────────────────────────────────────────
def quick_svg_avatar(output_path: str = "output/avatar.png") -> str:
    return generate_random_avatar(output_path)


# ────────────────────────────────────────
# Только портрет без talking (быстро)
# ────────────────────────────────────────
def quick_portrait_avatar(
    style: str = "realistic_woman",
    user_photo: str = None,
    output_path: str = "output/portrait_avatar.png"
) -> str:
    portrait = generate_portrait(style=style, output_path=output_path)
    if user_photo:
        swap_face(user_photo, portrait, output_path)
        enhance_face(output_path, output_path)
    return output_path


if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode == "svg":
        result = quick_svg_avatar()
        print(f"SVG аватар: {result}")

    elif mode == "portrait":
        result = quick_portrait_avatar(style="cyberpunk")
        print(f"Портрет: {result}")

    elif mode == "full":
        results = create_avatar_pipeline(
            script_text="Привет! Это мой аватар для коротких роликов.",
            avatar_style="cyberpunk",
            expression_scale=1.2,
        )
        print(f"Финальный аватар: {results['final_video']}")
```

---

## 13. Структура проекта и зависимости

### 13.1 Структура папок

```
avatar_engine/
│
├── avatar_engine.py          # Главный оркестратор
├── svg_avatar.py             # Уровень 0: SVG
├── portrait_generator.py     # Уровень 1: Stable Diffusion
├── face_swap.py              # Уровень 2: InsightFace swap
├── face_analyzer.py          # Уровень 3: DeepFace анализ
├── voice_cloner.py           # Уровень 6: XTTS / OpenVoice
├── sadtalker_wrapper.py      # Уровень 4: SadTalker
├── wav2lip_wrapper.py        # Уровень 5a: Wav2Lip
├── musetalk_wrapper.py       # Уровень 5b: MuseTalk
├── liveportrait_wrapper.py   # Уровень 7: LivePortrait
├── er_nerf_pipeline.py       # Уровень 8: ER-NeRF
├── postprocessing.py         # Постобработка
│
├── external/                 # git clone репозитории
│   ├── SadTalker/
│   ├── Wav2Lip/
│   ├── MuseTalk/
│   ├── LivePortrait/
│   ├── ER-NeRF/
│   └── CodeFormer/
│
├── models/                   # Веса моделей
│   ├── insightface/
│   │   └── inswapper_128.onnx
│   ├── GFPGANv1.4.pth
│   ├── RealESRGAN_x4plus.pth
│   └── er_nerf/              # Обученные NeRF-модели
│
├── assets/
│   ├── backgrounds/          # Кастомные фоны
│   └── luts/                 # LUT для цветокоррекции
│
├── temp/                     # Временные файлы (авточистка)
├── output/                   # Результаты
│
├── .env                      # API ключи
└── requirements.txt
```

### 13.2 requirements.txt

```
# Ядро
Pillow>=10.0.0
opencv-python>=4.8.0
numpy>=1.24.0
requests>=2.31.0
python-dotenv>=1.0.0

# SVG аватары
python-avatars>=1.3.0
cairosvg>=2.7.0

# Генерация изображений
diffusers>=0.27.0
transformers>=4.38.0
accelerate>=0.27.0
torch>=2.0.0
torchvision>=0.15.0

# Face analysis & swap
insightface>=1.0.0
deepface>=0.0.90
onnxruntime-gpu>=1.17.0

# Улучшение качества
gfpgan>=1.3.8
basicsr>=1.4.2
realesrgan>=0.3.0
facexlib>=0.3.0

# Удаление фона
rembg>=2.0.50

# Голос
TTS>=0.22.0  # XTTS v2
edge-tts>=6.1.9

# Утилиты
tqdm>=4.66.0
rich>=13.0.0

# Опциональные API
replicate>=0.25.0
```

### 13.3 Ссылки на модели

| Модель | Ссылка | Лицензия |
|---|---|---|
| SDXL | huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 | OpenRAIL |
| InsightFace inswapper | huggingface.co/deepinsight/inswapper | Non-commercial |
| GFPGANv1.4 | github.com/TencentARC/GFPGAN/releases | Apache 2.0 |
| SadTalker weights | huggingface.co/vinthony/SadTalker | CC BY-NC 4.0 |
| MuseTalk | huggingface.co/TMElyralab/MuseTalk | MIT |
| XTTS v2 | huggingface.co/coqui/XTTS-v2 | CPML (Non-commercial) |
| LivePortrait | huggingface.co/KwaiVGI/LivePortrait | MIT |
| RealESRGAN x4 | github.com/xinntao/Real-ESRGAN/releases | BSD 3-Clause |

---

## 14. Этические ограничения и лицензии

> ⚠️ Этот раздел — не формальность. Нарушение этих правил приводит к юридическим последствиям.

### Что можно

- Генерировать аватары на основе собственного фото
- Создавать персонажей для брендов и продуктов
- Анимировать публичные персоны для **документальных и образовательных** целей
- Использовать для контента, где **чётко указано** что это AI-генерация
- Исследовательские и некоммерческие проекты

### Что нельзя

- Создавать дипфейки реальных людей без их согласия
- Генерировать контент, вводящий в заблуждение о реальных событиях
- Использовать InsightFace inswapper и SadTalker в коммерческих продуктах (Non-commercial лицензии)
- Клонировать чужой голос без разрешения
- Создавать NSFW-контент с реальными людьми

### Маркировка AI-контента

```python
# watermark.py
from PIL import Image, ImageDraw, ImageFont

def add_ai_watermark(image_path: str, output_path: str = None) -> str:
    """Добавляет обязательную маркировку AI-generated."""
    output_path = output_path or image_path
    img = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    text = "AI Generated"
    try:
        font = ImageFont.truetype("assets/fonts/Montserrat-ExtraBold.ttf", 28)
    except:
        font = ImageFont.load_default()

    w, h = img.size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]

    # Белый текст с тёмной подложкой в правом нижнем углу
    x, y = w - text_w - 20, h - 50
    draw.rectangle([(x - 8, y - 4), (x + text_w + 8, y + 36)], fill=(0, 0, 0, 140))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 230))

    combined = Image.alpha_composite(img, overlay)
    combined.convert("RGB").save(output_path)
    return output_path
```

### Коммерческие альтернативы без лицензионных ограничений

| Задача | Инструмент | API |
|---|---|---|
| Talking avatar | D-ID | did.com/api |
| Lip sync | Sync Labs | synclabs.so |
| Voice clone | ElevenLabs | elevenlabs.io |
| Portrait gen | Leonardo.ai | leonardo.ai/api |
| Full avatar | HeyGen | heygen.com/api |

---

> **Совет по порядку разработки:**
> Начни с Уровня 0 (SVG) — работает везде без GPU. Затем Уровень 1+2 (SD + Face Swap) — это уже профессиональный результат для профилей и брендинга. Уровень 4 (SadTalker) добавляет главный WOW-эффект для Reels. Уровни 7–8 — только если аватар будет постоянным персонажем проекта и ты готов инвестировать время в настройку.
