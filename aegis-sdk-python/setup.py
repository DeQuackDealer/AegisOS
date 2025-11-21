from setuptools import setup, find_packages

setup(
    name='aegis-os-sdk',
    version='2.0.0',
    description='Official Python SDK for Aegis OS API',
    author='Aegis OS Team',
    author_email='sdk@aegis-os.dev',
    url='https://github.com/aegis-os/sdk-python',
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'python-dotenv>=0.20.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
