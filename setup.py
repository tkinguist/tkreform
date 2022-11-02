from setuptools import setup, find_packages

setup(
    name='tkreform',
    version=open("VERSION").read(),
    description='Reformed tkinter coding tool.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='HivertMoZara',
    author_email='worldmozara@gmail.com',
    url='https://github.com/tkinguist/tkreform',
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    extras_require={
        "PIL": ["Pillow>=2.7"]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    license='MIT',
)
