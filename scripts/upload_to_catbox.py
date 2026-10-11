#!/usr/bin/env python3
import urllib.request
import urllib.parse
from pathlib import Path

files = [
    Path("media/assets/carrossel_02_slide1.jpg"),
    Path("media/assets/carrossel_02_slide2.jpg"),
    Path("media/assets/carrossel_02_slide3.jpg"),
    Path("media/assets/carrossel_02_slide4.jpg"),
    Path("media/assets/carrossel_02_slide5.jpg"),
    Path("media/assets/carrossel_02_slide6.jpg"),
]

url = "https://catbox.moe/user/api.php"

for f in files:
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    data = []
    data.append(f"--{boundary}".encode())
    data.append(b'Content-Disposition: form-data; name="reqtype"')
    data.append(b'')
    data.append(b'fileupload')
    
    data.append(f"--{boundary}".encode())
    data.append(f'Content-Disposition: form-data; name="fileToUpload"; filename="{f.name}"'.encode())
    data.append(b'Content-Type: image/jpeg')
    data.append(b'')
    with open(f, 'rb') as fp:
        data.append(fp.read())
        
    data.append(f"--{boundary}--".encode())
    data.append(b'')
    
    body = b'\r\n'.join(data)
    
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'User-Agent': 'Mozilla/5.0'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            link = resp.read().decode('utf-8').strip()
            print(f"{f.name} => {link}")
    except Exception as e:
        print(f"Error uploading {f.name}: {e}")
