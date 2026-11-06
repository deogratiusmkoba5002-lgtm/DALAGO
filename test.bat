@echo off
REM Run all tests:            test.bat
REM Run one app:             test.bat fares
docker compose run --rm web python manage.py test %*
