import requests
url = "https://res.cloudinary.com/dxthallqr/image/upload/v1778041111/media/application_resumes/Aditya_Raj_Resume_ECE_zqet3f.pdf"
r = requests.head(url)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type', 'unknown')}")
print(f"Content-Length: {r.headers.get('content-length', 'unknown')}")
