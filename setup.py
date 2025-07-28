from setuptools import setup, find_packages

setup(
    name="tzbundler",
    version="1.0.0",
    description="IANA and Windows Zone Timezone Bundler",
    author="Iwan Kelaiah",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0"
    ],
    python_requires=">=3.8",
)