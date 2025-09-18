@echo off
echo Testing API connection...
curl -k -H "Authorization: Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70" https://127.0.0.1:27124/vault/
echo.
echo Test completed.
pause