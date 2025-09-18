@echo off
echo Testing Obsidian API with curl...
echo.

curl -k -H "Authorization: Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70" https://127.0.0.1:27124/vault/ > api_response.json

echo.
echo API response saved to api_response.json
echo.

type api_response.json

echo.
echo Press Enter to continue...
pause
