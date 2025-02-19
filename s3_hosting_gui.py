import os
import uuid
import boto3
import json
import zipfile

# إعدادات AWS
AWS_ACCESS_KEY = 'AKIAVIPZAYL4MT3TJM43'  # استبدل بمفتاح الوصول الخاص بك
AWS_SECRET_KEY = 'vDhpi4Ubjtt+NK0ZOIg+TxxIzMR22Uwt80DhXs+4'  # استبدل بمفتاح السر الخاص بك
BUCKET_NAME = "ghaymah-course-bucket"  # استبدل باسم الـ Bucket الخاص بك
REGION_NAME = 'us-east-2'  # استبدل بالمنطقة الخاصة بك
S3_FOLDER_NAME = "sherif/linux/"  # المجلد المحدد في S3

# تهيئة عميل S3
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)

# وظيفة لحذف الملفات القديمة من S3
def delete_existing_files():
    try:
        # الحصول على قائمة الملفات الموجودة في المجلد
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_FOLDER_NAME)
        if 'Contents' in response:
            for obj in response['Contents']:
                s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
                print(f"Deleted {obj['Key']} from S3.")
        return True
    except Exception as e:
        print(f"Error deleting files: {e}")
        return False

# وظيفة لرفع الملفات إلى S3
def upload_files_to_s3(folder_path):
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                local_path = os.path.join(root, file)
                s3_path = os.path.join(S3_FOLDER_NAME, os.path.relpath(local_path, folder_path))

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
                'ErrorDocument': {'Key': f'{S3_FOLDER_NAME}index.html'},
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
                    'Resource': [f'arn:aws:s3:::{BUCKET_NAME}/{S3_FOLDER_NAME}*']
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

# مثال لاستخدام البرنامج
if __name__ == '__main__':
    # مسار الملف المضغوط أو المجلد
    file_path = "path/to/your/zipfile_or_folder"

    # إنشاء مجلد مؤقت لاستخراج الملفات إذا كان الملف مضغوطًا
    temp_folder = os.path.join(os.getcwd(), str(uuid.uuid4()))
    os.makedirs(temp_folder, exist_ok=True)

    if file_path.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_folder)
    else:
        temp_folder = file_path

    # حذف الملفات القديمة من S3
    if delete_existing_files():
        print("Deleted existing files from S3.")

    # رفع الملفات إلى S3
    if upload_files_to_s3(temp_folder):
        # تكوين استضافة S3
        if configure_s3_hosting():
            print(f"Website hosted at: http://{BUCKET_NAME}.s3-website.{REGION_NAME}.amazonaws.com/{S3_FOLDER_NAME}")
        else:
            print("Failed to configure S3 hosting.")
    else:
        print("Failed to upload files to S3.")