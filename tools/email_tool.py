import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_application_email(to_email: str, subject: str, body: str, attachment_path: str) -> str:
    """
    Sends a real application email with the tailored CV attached using SMTP.
    """
    # Ước tính số token của nội dung email nhận được từ Agent 2
    estimated_tokens = len(body) / 4
    print(f"[METRICS] Estimated Output Email Tokens: {estimated_tokens}")
    estimated_body_tokens = round(len(body) / 4)
    print(f"📊 [Captured Token Metrics via Tool] Estimated Output Body Tokens: {estimated_body_tokens}")
    
    # Lấy thông tin tài khoản từ biến môi trường để đảm bảo bảo mật (Day 4 Security)
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD") # Đây phải là App Password, không phải mật khẩu chính
    
    if not sender_email or not sender_password:
        return "Error: Missing SENDER_EMAIL or SENDER_PASSWORD environment variables."

    if not os.path.exists(attachment_path):
        return f"Error: Cannot find attachment at {attachment_path}"

    try:
        # 1. Thiết lập cấu trúc Email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # 2. Đính kèm file CV
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)

        # 3. Kết nối đến Máy chủ Gmail SMTP và gửi
        print(f"[SMTP] Connecting to Gmail server to send email to {to_email}...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls() # Bảo mật kết nối
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()

        return f"Success: Real email successfully sent to {to_email} with CV attached!"

    except Exception as e:
        return f"SMTP Error occurred: {str(e)}"