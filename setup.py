from setuptools import setup, find_packages

setup(
    name='SSD1306',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['smbus2', 'Pillow'],
    description='A library for SSD1306 OLED displays with I2C',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    url='https://github.com/LuceZi/Luce_ssd1306',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
