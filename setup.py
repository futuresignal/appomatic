from setuptools import setup, find_packages

install_requires = [
]

setup(
    name='Appomatic',
    version='0.1',
    description='Automated Golang DB Interface Code Generation',
    author='Blake Allen',
    author_email='blakedallen@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'appomatic = appomatic.appomatic:main',            
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
