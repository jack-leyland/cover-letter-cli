from setuptools import setup, find_packages
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
setup(
    name = 'coverletter',
    version = '0.0.1',
    author = 'Jack Leylad',
    author_email = 'jack@leyland.dev',
    license = 'MIT',
    description = 'Small templating tool for quicker cover letters.',
    url = 'https://github.com/jack-leyland/cover-letter-cli',
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        coverletter=coverletter.main:run
    '''
)