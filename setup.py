from setuptools import setup, find_packages

setup(
    name="usbGPStoCot",
    version="1.0.0",
    description="USB GPS CoT Transmitter for TAK Protocol v1",
    author="JR@myTeckNet",
    author_email="support@mytecknet.com",
    url="https://github.com/myTeckNet/usbGPStoCoT.git",
    py_modules=["usbGPStoCot"],
    install_requires=[
        "pyserial",
        "pynmea2"
    ],
    entry_points={
        "console_scripts": [
            "usbGPStoCot=usbGPStoCot:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)