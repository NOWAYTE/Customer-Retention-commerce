from setuptools import setup, find_packages

setup(
    name="crm_app",
    version="0.1",
    packages=find_packages(include=['app*', 'tests*']),
    include_package_data=True,
    install_requires=[
        'Flask>=2.0.0',
        'Flask-SQLAlchemy>=2.5.0',
        'Flask-Migrate>=3.1.0',
        'Flask-Login>=0.5.0',
        'gunicorn>=20.1.0',
        'scikit-learn>=1.0.0',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'python-dotenv>=0.19.0',
        'pytest>=6.2.5',
        'pytest-cov>=3.0.0'
    ],
    python_requires='>=3.8',
)
