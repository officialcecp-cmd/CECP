import requests

url = "https://res.cloudinary.com/dxthallqr/raw/upload/v1778046868/media/application_resumes/Aditya_Raj_Resume_ECE_y7rbim.pdf"
r = requests.get(url)
print(f"Status: {r.status_code}")
print(f"Headers: {r.headers}")
print(f"Content: {r.text[:200]}")
