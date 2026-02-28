# ELS JUDGE

**Built by [codedbyelif](https://github.com/codedbyelif)**

A production-ready application that evaluates and improves code using multiple large language models. The engine sends your code and instructions to GPT-4o, Claude 3.5, and Gemini Pro simultaneously, collects their improved versions, and shows you a side-by-side comparison of what each AI changed.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/codedbyelif/els-judge.git
cd els-judge
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Create a `.env` file in the project root and add your API keys:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...
```

### 5. Run the project

```bash
bash start.sh
```

This starts both the FastAPI backend (port 8000) and the Streamlit dashboard (port 8501).

### 6. Open in browser

- **Dashboard:** http://localhost:8501
- **API Docs (Swagger):** http://localhost:8000/docs

---

## How to Use

1. Open the dashboard at http://localhost:8501
2. Paste your code in the **"Your Code"** text area
3. Write what you want improved in the **"What should be improved?"** input (e.g., "Make this code more secure", "Optimize performance", "Add error handling")
4. Click **"Analyze with 3 AI Models"**
5. View each model's suggestions in separate tabs:
   - What they changed and why
   - Before/after code comparison
   - Full diff view
   - Complete improved code

### Terminal Dashboard (CLI)

If you prefer the terminal, you can use our beautifully styled TUI (Terminal User Interface):

1. Make sure your `FastAPI` backend is running (`bash start.sh` or `uvicorn main:app`).
2. Run the CLI tool:
   ```bash
   python cli.py
   ```
3. Paste your code, press `Enter`, then type `END` on a new line.
4. Provide your prompt and watch the AI analyze your code directly in the terminal!

---

## Architecture Patterns (Inspired by Microsoft LLM-as-Judge)

This project was inspired by Microsoft's open-source **LLM-as-Judge** framework. Below is a detailed analysis of the patterns we adopted and why.

### What We Adopted

| Pattern | Source (Microsoft) | Our Implementation | Why |
|---------|-------------------|-------------------|-----|
| **CORS Middleware** | `main.py` CORSMiddleware | `main.py` Same config | Allows dashboard and external clients to access the API without cross-origin errors |
| **Structured Error Responses** | `schemas/responses.py` ErrorMessage | `main.py` validation_exception_handler | Users get consistent, readable error messages instead of raw stack traces |
| **Validation Exception Handlers** | `main.py` Custom exception handler | `main.py` Same pattern | Prevents raw 422 errors; provides user-friendly messages |
| **Field Validators** | `schemas/models.py` field_validator | `schemas/api.py` field_validator | Catches invalid inputs early before they reach the LLM pipeline |
| **Parallel Judge Execution** | `judges.py` asyncio.gather for judges | `engine/dispatcher.py` asyncio.gather for 3 LLMs | All 3 models run simultaneously, reducing wait time by ~3x |
| **Orchestrator Pattern** | `judges.py` JudgeOrchestrator | `engine/dispatcher.py` process_submission | Single entry point that coordinates the entire pipeline |

### What We Did NOT Adopt (and Why)

| Pattern | Why Not |
|---------|---------|
| **Azure Cosmos DB** | We use SQLite for simplicity, no cloud dependency needed |
| **Semantic Kernel / ChatCompletionAgent** | We use LiteLLM which supports OpenAI, Anthropic, and Google through a single interface |
| **SuperJudge / Mediator Pattern** | Our system improves code, it doesn't judge quality. No need for a "judge of judges" |
| **Judge Assembly / CRUD endpoints** | We have 3 fixed models configured via .env, no dynamic management needed |
| **Terraform / Azure Container Apps** | Not needed for our local/Docker setup |
| **Statistical Analysis Plugin** | We show code diffs, not statistical metrics |
| **Clustering Plugin** | ML clustering, completely unrelated to our use case |

---

## Hizli Baslangic (Turkce)

### 1. Repoyu klonlayin

```bash
git clone https://github.com/codedbyelif/els-judge.git
cd els-judge
```

### 2. Sanal ortam olusturun

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Bagimliliklari yukleyin

```bash
pip install -r requirements.txt
```

### 4. API anahtarlarini yapilandirin

Proje kokunde bir `.env` dosyasi olusturun:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...
```

### 5. Projeyi calistirin

```bash
bash start.sh
```

Bu komut hem FastAPI backend'i (port 8000) hem de Streamlit dashboard'u (port 8501) baslatir.

### 6. Tarayicida acin

- **Dashboard:** http://localhost:8501
- **API Dokumantasyonu:** http://localhost:8000/docs

---

## Nasil Kullanilir

1. Dashboard'u http://localhost:8501 adresinden acin
2. Kodunuzu **"Kodun"** alanina yapistirin
3. Ne iyilestirilmesini istediginizi **"Ne iyilestirilsin?"** alanina yazin (ornek: "Bu kodu daha guvenli yap", "Performansi optimize et", "Hata yonetimi ekle")
4. **"3 AI Modeli ile Analiz Et"** butonuna tiklayin
5. Her modelin onerilerini ayri sekmelerden gorun:
   - Ne degistirdi ve neden
   - Oncesi/sonrasi kod karsilastirmasi
   - Tam fark gorunumu
   - Tamamlanmis iyilestirilmis kod

### Terminal Arayuzu (TUI)

Eger islerinizi terminalden yurutmeyi tercih ediyorsaniz, ozel tasarimli TUI (Terminal User Interface) aracimizi kullanabilirsiniz:

1. `FastAPI` sunucusunun arkaplanda calistigindan emin olun (`bash start.sh` veya `uvicorn main:app`).
2. Yeni bir terminal penceresinde CLI aracini baslatin:
   ```bash
   python cli.py
   ```
3. Acilan ekranda sol panele kodunuzu yapistirin ve enter'a basin.
4. Alt kisimdaki alana promptunuzu (istem) yazin.
5. `CTRL+R` kisayoluyla veya butona tiklayarak 3 AI modelinin analizini dogrudan terminalinizde baslatin!

## Docker Kurulumu (Alternatif)

Eğer projeyi izole Docker container'ları içinde çalıştırmayı tercih ederseniz, `docker-compose` kullanabilirsiniz:

### 1. API Anahtarlarını Ayarlayın
Lokal kurulumda olduğu gibi öncelikle bir `.env` dosyasına ihtiyacınız var:
```bash
cp .env.example .env  # Veya kendiniz bir .env dosyasi olusturun
```
İçerisine API anahtarlarınızı girin:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...
```

### 2. Başlatın
Proje ana dizininde şu komutu çalıştırın:
```bash
docker-compose up --build -d
```
Docker Compose `.env` dosyanızı otomatik okuyarak sistemdeki iki container'ı (API ve Arayüz) başlatacaktır.

### 3. Tarayıcıda Açın
- **Dashboard:** http://localhost:8501
- **API Dokümantasyonu:** http://localhost:8000/docs
- **Logları İzlemek:** `docker-compose logs -f`
- **Sistemi Durdurmak:** `docker-compose down`

---

## Mimari Desenleri (Microsoft LLM-as-Judge'dan Esinlenildi)

### Aldigimiz Desenler

| Desen | Neden Aldik |
|-------|-------------|
| **CORS Middleware** | Dashboard ve dis istemcilerin API'ye cross-origin hatasi olmadan erisebilmesi icin |
| **Yapilandirilmis Hata Yanitlari** | Kullanicilar ham hata mesajlari yerine okunabilir JSON hatalari alir |
| **Dogrulama Istisna Isleyicileri** | Pydantic dogrulama hatalarini yakalar ve kullanici dostu mesajlar sunar |
| **Alan Dogrulayicilari** | Gecersiz girisleri LLM pipeline'ina ulasmadan once yakalir |
| **Paralel Model Calistirma** | 3 model sirayla degil ayni anda calisir, toplam bekleme suresini ~3 kat azaltir |
| **Orkestrator Deseni** | Tum pipeline'i koordine eden tek bir giris noktasi |

### Almadigimiz Desenler

| Desen | Neden Almadik |
|-------|--------------|
| **Azure Cosmos DB** | Yerel gelistirme icin SQLite daha basit |
| **Semantic Kernel** | LiteLLM tek bir arayuzle 3 farkli AI saglayicisini destekliyor |
| **SuperJudge / Araci Deseni** | Biz kodu iyilestiriyoruz, degerlendirmiyoruz, "yargiclarin yargici" gerekmiyor |
| **CRUD Endpointleri** | Sabit 3 model kullaniyoruz, dinamik yapilandirma gerekmiyor |

---

## Project Structure

```
ai-code-judge/
  main.py              # FastAPI app + CORS + error handlers
  start.sh             # Branded launcher script
  requirements.txt     # Python dependencies
  .env                 # API keys (not committed)
  core/
    config.py          # Settings and environment variables
    database.py        # SQLAlchemy engine and session
  models/
    domain.py          # Database models (Submission, ModelSuggestion)
  schemas/
    api.py             # Pydantic schemas with field validators
  engine/
    reviewers.py       # LiteLLM multi-model code improvement
    diff_analyzer.py   # Unified diff generation
    aggregator.py      # Cross-model comparison
    reporter.py        # Markdown report generation
    dispatcher.py      # Pipeline orchestrator
  api/
    routes.py          # FastAPI REST endpoints
  dashboard/
    app.py             # Streamlit UI (dark pink theme)
    translations.py    # EN/TR language support
```

---

## Docker Setup

If you prefer to run the entire stack in isolated Docker containers, you can use the provided Docker Compose configuration. This will spin up two containers: one for the FastAPI backend and one for the Streamlit dashboard.

### 1. Configure API Keys
Just like the local setup, you need a `.env` file first:
```bash
cp .env.example .env  # Or simply create a .env file
```
Add your keys inside `.env`:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...
```

### 2. Build and Run Container
Run the following command in the root of the project:
```bash
docker-compose up --build -d
```
Docker Compose will automatically read your `.env` variables and pass them to the containers.

### 3. Open in Browser
- **Dashboard:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **View Logs:** `docker-compose logs -f`
- **Stop Containers:** `docker-compose down`

---

**Built by [codedbyelif](https://github.com/codedbyelif)** | ELS JUDGE v1.0
