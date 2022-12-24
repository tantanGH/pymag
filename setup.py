import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymag",
    version="0.0.4",
    author="tantanGH",
    author_email="tantanGH@github",
    license='MIT',
    description="MAG image format utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tantanGH/pymag",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pymag=pymag.pymag:main'
        ]
    },
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    setup_requires=["Pillow"],
)
