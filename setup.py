from setuptools import setup, find_packages

setup(
    name="face_recognition",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "streamlit",
        "streamlit-option-menu",
        "pandas",
        "firebase-admin",
        "python-dotenv",
    ],
)
