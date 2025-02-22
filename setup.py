from setuptools import setup, find_packages

setup(
    name="trendyol_project",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-migrate',
        'flask-limiter',
        'flask-cors',
        'pyjwt',
        'python-dotenv'
    ]
) 