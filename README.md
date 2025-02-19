# S3 Hosting GUI

A simple GUI application to upload files to an AWS S3 bucket and configure it for static website hosting.

## Requirements

Ensure you have the following installed:

1. **Python 3.x**: Required to run the script.
2. **Boto3**: AWS SDK for Python. Install it via pip:
   ```bash
   pip install boto3
   ```
3. **Tkinter**: Typically pre-installed with Python. If not, install it using:
   ```bash
   sudo apt-get install python3-tk
   ```
4. **python-dotenv**: To manage environment variables. Install it using:
   ```bash
   pip install python-dotenv
   ```
5. **AWS Credentials**: Store your AWS Access Key and Secret Key securely in a `.env` file.

## Setup

1. Clone the repository or download the script.
2. Create a `.env` file in the project directory and add the following details:
   ```plaintext
   AWS_ACCESS_KEY=your_access_key
   AWS_SECRET_KEY=your_secret_key
   BUCKET_NAME=your_bucket_name
   FOLDER_NAME=your_folder_name/
   AWS_REGION=your_aws_region
   ```
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Run the script using:
```bash
python s3_hosting_gui.py
```

A GUI window will appear with the following functionalities:
- Use the **Browse** button to select a folder to upload.
- Click **Upload and Configure** to upload files and configure S3 for static hosting.
- Once the process is complete, the website URL will be displayed.
- Use the **Copy** button to copy the website URL.

## Notes

- Ensure your AWS credentials have the necessary permissions to upload files and configure S3 bucket settings.
- The application will **delete any existing files** in the specified folder before uploading new ones.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## `requirements.txt`

```plaintext
boto3==1.26.0
python-dotenv==0.21.0
```

### How to Run

1. **Create a `.env` file**: Store AWS credentials and bucket details as shown in the setup section.
2. **Install dependencies**: Run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**: Execute:
   ```bash
   python s3_hosting_gui.py
   ```
4. **Use the GUI**: Follow the instructions to select a folder, upload files, and configure S3 hosting.

