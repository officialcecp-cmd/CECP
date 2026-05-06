import cloudinary
import cloudinary.api
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

public_id = 'media/application_resumes/Aditya_Raj_Resume_ECE_zqet3f'

# Check as image
try:
    result = cloudinary.api.resource(public_id, resource_type='image')
    print("Found as IMAGE:")
    print("  URL:", result.get("secure_url"))
    print("  Format:", result.get("format"))
    print("  Type:", result.get("resource_type"))
    print("  Bytes:", result.get("bytes"))
except Exception as e:
    print("Not found as image:", str(e)[:200])

# Check as raw
try:
    result = cloudinary.api.resource(public_id, resource_type='raw')
    print("Found as RAW:")
    print("  URL:", result.get("secure_url"))
except Exception as e:
    print("Not found as raw:", str(e)[:200])

# List all resources in application_resumes folder
print("\n--- Searching all resources in application_resumes/ ---")
try:
    result = cloudinary.api.resources(type='upload', prefix='media/application_resumes', resource_type='image', max_results=10)
    for r in result.get('resources', []):
        print(f"  IMAGE: {r['public_id']} (format={r.get('format')}, url={r.get('secure_url')})")
except Exception as e:
    print("  Image search error:", str(e)[:200])

try:
    result = cloudinary.api.resources(type='upload', prefix='media/application_resumes', resource_type='raw', max_results=10)
    for r in result.get('resources', []):
        print(f"  RAW: {r['public_id']} (url={r.get('secure_url')})")
except Exception as e:
    print("  Raw search error:", str(e)[:200])
