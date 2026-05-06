import cloudinary
import cloudinary.utils
import cloudinary.api
import requests
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

public_id = 'media/application_resumes/Aditya_Raj_Resume_ECE_y7rbim.pdf'

# Generate signed URL for raw
url, options = cloudinary.utils.cloudinary_url(
    public_id,
    resource_type='raw',
    sign_url=True
)
print("Signed RAW URL:", url)

r = requests.head(url)
print(f"Status: {r.status_code}")

url2, options2 = cloudinary.utils.cloudinary_url(
    public_id,
    resource_type='raw'
)
print("Unsigned RAW URL:", url2)

r2 = requests.head(url2)
print(f"Status: {r2.status_code}")

# Can we download it via admin API?
try:
    res = cloudinary.api.resource(public_id, resource_type='raw')
    print("Found via API!")
    print(res.get('secure_url'))
except Exception as e:
    print("API Error:", e)

