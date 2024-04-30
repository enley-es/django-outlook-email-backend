from distutils.core import setup

setup(
    name='django-outlook-email-backend',
    version='0.3.8',
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
)