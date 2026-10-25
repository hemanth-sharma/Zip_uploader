Uploads files and zip

run: uvicorn main:app --host 127.0.0.1 --port 8000 --reload
upload at: curl -X 'POST' `
  'http://127.0.0.1:8000/upload' `
  -H 'Authorization: Bearer my-unique-ai-secret-key' `
  -F 'file=@path/to/your/document.zip'

And tunnel URL startup: 
ngrok.exe 