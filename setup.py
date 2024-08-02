from setuptools import setup, find_packages

def load_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]
    
setup(
    name="koi",
    version=0.1,
    url="https://github.com/BlockScience/koi-api/",
    author="Luke Miller",
    author_email="luke@block.science",
    packages=find_packages(),
    install_requires=load_requirements()
)