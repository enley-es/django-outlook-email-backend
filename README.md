# Django outlook email backend
### Outlook api email backend for Django

## Requirements
- Python 3.8+
- Django 5.0, 4.2

## Installation
Install using pip...
```commandline
pip install django-outlook-email-backend
```
Add  `'OUTLOOK_CREDENTIALS'` in `settings.py`  
```python
OUTLOOK_CREDENTIALS = {
    'OUTLOOK_CLIENT_ID': "XXXXX",
    'OUTLOOK_CLIENT_SECRET': "XXXXX",
    'OUTLOOK_TENANT_ID': "XXXXX",
}
```

Add  `'EMAIL_BACKEND'` in `settings.py`  

```python
EMAIL_BACKEND = "django_outlook_email.django_outlook_email_backend.OutlookEmailBackend"
``` 

if you want to use json instead of mime the add the following line in in `settings.py`
```python
OUTLOOK_CREDENTIALS["OUTLOOK_SEND_FORMAT"] = "json"
```