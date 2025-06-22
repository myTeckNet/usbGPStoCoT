from setuptools import setup, find_packages

setup(
    name="usbGPStoCoT",
    version="1.0.0",
    description="USB GPS CoT Transmitter for TAK Protocol v1",
    author="JR@myTeckNet",
    author_email="support@mytecknet.com",
    url="https://github.com/myTeckNet/usbGPStoCoT.git",
    py_modules=["usbGPStoCoT"],
    install_requires=[
        "pyserial",
        "pynmea2"
    ],
    entry_points={
        "console_scripts": [
            "usbGPStoCoT=usbGPStoCoT:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)