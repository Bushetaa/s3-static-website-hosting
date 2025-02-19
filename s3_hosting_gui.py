import os
import boto3
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import threading
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# إعدادات AWS
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')
FOLDER_NAME = os.getenv('FOLDER_NAME')
AWS_REGION = os.getenv('AWS_REGION')

# تهيئة عميل S3
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# وظيفة لحذف الملفات القديمة من S3
def delete_existing_files(folder_name):
    try:
        # الحصول على قائمة الملفات الموجودة في المجلد
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder_name)
        if 'Contents' in response:
            for obj in response['Contents']:
                s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
                print(f"Deleted {obj['Key']} from S3.")
        return True
    except Exception as e:
        print(f"Error deleting files: {e}")
        return False

# وظيفة لرفع الملفات إلى S3
def upload_files_to_s3(folder_path, folder_name):
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                local_path = os.path.join(root, file)
                s3_path = os.path.join(folder_name, os.path.relpath(local_path, folder_path))

                # تعيين نوع المحتوى بناءً على امتداد الملف
                if file.endswith('.html'):
                    content_type = 'text/html'
                elif file.endswith('.css'):
                    content_type = 'text/css'
                elif file.endswith('.js'):
                    content_type = 'application/javascript'
                elif file.endswith('.png'):
                    content_type = 'image/png'
                elif file.endswith('.jpg') or file.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif file.endswith('.svg'):
                    content_type = 'image/svg+xml'
                else:
                    content_type = 'application/octet-stream'

                s3.upload_file(local_path, BUCKET_NAME, s3_path, ExtraArgs={'ContentType': content_type})
                print(f"Uploaded {local_path} to {s3_path} with ContentType: {content_type}")
        return True
    except Exception as e:
        print(f"Error uploading files: {e}")
        return False

# وظيفة لتكوين استضافة S3
def configure_s3_hosting():
    try:
        # تفعيل استضافة الموقع
        s3.put_bucket_website(
            Bucket=BUCKET_NAME,
            WebsiteConfiguration={
                'ErrorDocument': {'Key': f'{FOLDER_NAME}index.html'},  # الصفحة الرئيسية داخل المجلد
                'IndexDocument': {'Suffix': 'index.html'}
            }
        )

        # ضبط سياسة الـ Bucket للوصول العام
        policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'PublicReadGetObject',
                    'Effect': 'Allow',
                    'Principal': '*',
                    'Action': ['s3:GetObject'],
                    'Resource': [f'arn:aws:s3:::{BUCKET_NAME}/{FOLDER_NAME}*']  # الوصول إلى الملفات داخل المجلد
                }
            ]
        }
        s3.put_bucket_policy(Bucket=BUCKET_NAME, Policy=json.dumps(policy))

        # تعطيل حظر الوصول العام
        s3.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )

        print("S3 bucket configured for static hosting.")
        return True
    except Exception as e:
        print(f"Error configuring S3 hosting: {e}")
        return False

# وظيفة لاختيار الملفات أو المجلدات
def select_files():
    folder_path = filedialog.askdirectory(title="Select Folder to Upload")
    if folder_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder_path)

# وظيفة لرفع الملفات وتكوين الاستضافة
def upload_and_configure():
    folder_path = entry_path.get()
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder to upload.")
        return

    # حذف الملفات القديمة من S3
    if delete_existing_files(FOLDER_NAME):
        print("Deleted existing files from S3.")

    # رفع الملفات إلى S3
    if upload_files_to_s3(folder_path, FOLDER_NAME):
        # تكوين استضافة S3
        if configure_s3_hosting():
            # إنشاء الرابط
            url = f"http://{BUCKET_NAME}.s3-website.{AWS_REGION}.amazonaws.com/{FOLDER_NAME}"
            print(f"Website hosted at: {url}")
            entry_url.delete(0, tk.END)
            entry_url.insert(0, url)
            messagebox.showinfo("Success", "Files uploaded and hosting configured successfully!")
        else:
            messagebox.showerror("Error", "Failed to configure S3 hosting.")
    else:
        messagebox.showerror("Error", "Failed to upload files to S3.")

# وظيفة لنسخ الرابط
def copy_url():
    url = entry_url.get()
    if url:
        root.clipboard_clear()
        root.clipboard_append(url)
        messagebox.showinfo("Copied", "URL copied to clipboard!")

# إنشاء واجهة المستخدم
root = tk.Tk()
root.title("S3 Hosting GUI")
root.geometry("500x300")
root.configure(bg="#2d2d2d")  # خلفية داكنة

# إطار لإدخال المسار
frame_path = tk.Frame(root, bg="#2d2d2d")
frame_path.pack(pady=10)

label_path = tk.Label(frame_path, text="Select Folder:", bg="#2d2d2d", fg="#ffffff")  # نص أبيض
label_path.pack(side=tk.LEFT, padx=5)

entry_path = tk.Entry(frame_path, width=40, bg="#3d3d3d", fg="#ffffff", insertbackground="white")  # خلفية داكنة ونص أبيض
entry_path.pack(side=tk.LEFT, padx=5)

button_browse = tk.Button(frame_path, text="Browse", command=select_files, bg="#4CAF50", fg="white")
button_browse.pack(side=tk.LEFT, padx=5)

# إطار لعرض الرابط
frame_url = tk.Frame(root, bg="#2d2d2d")
frame_url.pack(pady=10)

label_url = tk.Label(frame_url, text="Website URL:", bg="#2d2d2d", fg="#ffffff")  # نص أبيض
label_url.pack(side=tk.LEFT, padx=5)

entry_url = tk.Entry(frame_url, width=40, bg="#3d3d3d", fg="#ffffff", insertbackground="white")  # خلفية داكنة ونص أبيض
entry_url.pack(side=tk.LEFT, padx=5)

button_copy = tk.Button(frame_url, text="Copy", command=copy_url, bg="#2196F3", fg="white")
button_copy.pack(side=tk.LEFT, padx=5)

# زر الرفع
button_upload = tk.Button(root, text="Upload and Configure", command=upload_and_configure, bg="#FF9800", fg="white")
button_upload.pack(pady=20)

# تشغيل الواجهة
root.mainloop()
