from distutils.core import setup

setup(
    name='django_outlook_email-backend',
    version='1.1.16',
    description='Ouauth2 outlook email backend for Django',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Marc Claramunt',
    author_email='mclaramunt@enley.com',
    license='MIT',
    zip_safe=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url='https://github.com/enley-es/django-outlook-email-backend',
    packages=["django_outlook_email","django_outlook_email.exceptions", "django_outlook_email.senders","django_outlook_email.senders.attachments","django_outlook_email.senders.microsoft_requests","django_outlook_email.senders.encoders"],
    install_requires = ['requests~=2.25', 'msal==1.*']
)