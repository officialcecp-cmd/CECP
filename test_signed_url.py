import cloudinary
import cloudinary.utils
import requests
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

public_id = 'media/application_resumes/Aditya_Raj_Resume_ECE_zqet3f'

url, options = cloudinary.utils.cloudinary_url(
    public_id,
    resource_type='image',
    format='pdf',
    sign_url=True
)
print("Signed URL:", url)

r = requests.head(url)
print(f"Status: {r.status_code}")

url2, options2 = cloudinary.utils.cloudinary_url(
    public_id,
    resource_type='image',
    format='pdf',
    flags='attachment'
)
print("Attachment URL:", url2)

r2 = requests.head(url2)
print(f"Attachment Status: {r2.status_code}")
