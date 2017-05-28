from setuptools import setup, find_packages


setup(
    name='asynqp-consumer',
    version='0.2.1',
    author='Timofey Kukushkin',
    author_email='tima@kukushkin.me',
    url='https://github.com/tkukushkin/asynqp-consumer',
    description='Consumer utility class for AMQP',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'asynqp >= 0.5.1',
    ],
    extras_require={
        'test': [
            'pycodestyle',
            'pylint',
            'pytest==3.0.7',
            'pytest-asyncio==0.5.0',
            'pytest-cov==2.5.1',
            'pytest-mock==1.6.0',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Telecommunications Industry",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking"
    ]
)
