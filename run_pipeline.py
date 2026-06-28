import os
import json
import sys
import io
import re
import time
import yaml
from google import genai

# Cau hinh stdout de xu ly muot ma ky tu UTF-8 tren Windows Terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Nap cac bien moi truong tu file .env neu co
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

# Khai bao cac thong tin bao mat va cau hinh he thong
os.environ["GEMINI_API_KEY"] = os.environ.get("SENDER_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
os.environ["SENDER_EMAIL"] = os.environ.get("SENDER_EMAIL", "your_email@example.com")
os.environ["SENDER_PASSWORD"] = os.environ.get("SENDER_PASSWORD", "your_app_password_here")

# Khoi tao Client ket noi voi Gemini API
client = genai.Client()

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def estimate_tokens(text):
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    return max(int(words * 1.35), int(chars / 3.8)) + 120

def run_my_custom_pipeline():
    print("[SYSTEM] Starting AutoApply-Agent Pipeline via Python SDK...")
    sys.stdout.flush()
    
    # 0. Doc du lieu dau vao
    cv_content = read_file("cv_short.txt")
    jd_content = read_file("jd_short.txt")
    
    # Load model from config.yaml
    TARGET_MODEL = 'gemini-2.5-flash'
    if os.path.exists("config.yaml"):
        try:
            with open("config.yaml", "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
                if config_data and "model" in config_data:
                    TARGET_MODEL = config_data["model"]
        except Exception:
            pass
    
    # Khoi tao bien luu tru so lieu thong ke
    in_t1, out_t1, in_t2, out_t2 = 0, 0, 0, 0
    
    # =========================================================================
    # GIAI DOAN 1: CHAY AGENT TUY CHINH CV (CV TAILOR)
    # =========================================================================
    print("\n[Executing] Phase 1: CV Tailor Agent...")
    sys.stdout.flush()
    
    agent1_instruction = read_file("agents/cv_tailor.md")
    prompt_phase_1 = f"{agent1_instruction}\n\nUser Master CV:\n{cv_content}\n\nTarget Job Description:\n{jd_content}"
    
    response_agent1 = client.models.generate_content(
        model=TARGET_MODEL,
        contents=prompt_phase_1
    )
    tailored_cv = response_agent1.text
    
    try:
        in_t1 = response_agent1.usage_metadata.prompt_token_count
        out_t1 = response_agent1.usage_metadata.candidates_token_count
        if not in_t1 or not out_t1: raise Exception()
    except:
        in_t1 = estimate_tokens(prompt_phase_1)
        out_t1 = estimate_tokens(tailored_cv)

    print("[METRICS] Agent 1 Processed Successfully.")
    sys.stdout.flush()
    
    # Tam dung 1.5 giay de dong log Phase 1 hien thi ro rang
    time.sleep(1.5)

    # =========================================================================
    # GIAI DOAN 2: CHAY AGENT SOAN EMAIL (MAIL WRITER)
    # =========================================================================
    print("\n[Executing] Phase 2: Cover Letter & Mail Writer Agent...")
    sys.stdout.flush()
    
    agent2_instruction = read_file("agents/mail_writer.md")
    prompt_phase_2 = f"{agent2_instruction}\n\nTarget JD:\n{jd_content}\n\nTailored CV Output:\n{tailored_cv}"
    
    response_agent2 = client.models.generate_content(
        model=TARGET_MODEL,
        contents=prompt_phase_2
    )
    raw_output = response_agent2.text.strip()
    
    try:
        in_t2 = response_agent2.usage_metadata.prompt_token_count
        out_t2 = response_agent2.usage_metadata.candidates_token_count
        if not in_t2 or not out_t2: raise Exception()
    except:
        in_t2 = estimate_tokens(prompt_phase_2)
        out_t2 = estimate_tokens(raw_output)

    print("[METRICS] Agent 2 Processed Successfully.")
    sys.stdout.flush()
    
    # Tam dung 1.5 giay truoc khi vao Gatekeeper kiem duyet
    time.sleep(1.5)

    # --- TRICH XUAT JSON AN TOAN ---
    email_subject = "Application for Senior Business Analyst - Tran Viet Nhan"
    email_body = raw_output

    json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
    if json_match:
        clean_json_str = json_match.group(0)
        try:
            json_data = json.loads(clean_json_str)
            if "subject" in json_data:
                email_subject = json_data["subject"]
            if "body" in json_data:
                email_body = json_data["body"]
        except Exception:
            email_body = raw_output

    # =========================================================================
    # GIAI DOAN 3: TRAM KIEM SOAT BAO MAT VA XAC NHAN (GATEKEEPER)
    # =========================================================================
    print("\n[Executing] Phase 3: Gatekeeper Agent (Human-in-the-Loop)...")
    print("-" * 60)
    print(f"PROPOSED EMAIL SUBJECT: {email_subject}")
    print("\nPROPOSED EMAIL BODY:")
    print(email_body)
    print("-" * 60)
    sys.stdout.flush()
    
    user_choice = input("Should I go ahead and send this application email to the enterprise? (Yes/No): ")
    
    if user_choice.strip().lower() in ['yes', 'y', 'confirm']:
        from tools.email_tool import send_application_email
        
        with open("tailored_cv.txt", "w", encoding="utf-8") as f:
            f.write(tailored_cv)
            
        result = send_application_email(
            to_email="tvietnhan@gmail.com",
            subject=email_subject,
            body=email_body,
            attachment_path="tailored_cv.txt"
        )
        print(f"\n[Tool Result] {result}")
    else:
        print("\n[Cancelled] Deployment stopped. No email was sent.")

    # =========================================================================
    # PHAN TONG KET THONG KE TOKEN CUOI CUNG
    # =========================================================================
    total_input = in_t1 + in_t2
    total_output = out_t1 + out_t2
    
    print("\n" + "="*50)
    print("      PIPELINE EXECUTION SUMMARY & TOKEN METRICS")
    print("="*50)
    print(f"  Agent 1 (CV Tailor)   -> Input: {in_t1} | Output: {out_t1} tokens")
    print(f"  Agent 2 (Mail Writer) -> Input: {in_t2} | Output: {out_t2} tokens")
    print("-" * 50)
    print(f"  TOTAL INPUT CONTEXT   : {total_input} tokens")
    print(f"  TOTAL OUTPUT GENERATED: {total_output} tokens")
    print(f"  INFRASTRUCTURE MODEL  : {TARGET_MODEL}")
    print("="*50)
    sys.stdout.flush()

if __name__ == "__main__":
    run_my_custom_pipeline()