"""Module setuptools script."""
from setuptools import setup

description = """
"""

setup(
    name='autoLeague',
    version='1.0.0',
    description='autoLeague League of Legends dataset settings library',
    long_description=description,
    long_description_content_type="text/markdown",
    author='hanueluni1106',
    author_email='sykim1106@naver.com',
    license='MIT License',
    keywords=[
        'League of Legends',
        'Machine Learning',
        'Reinforcement Learning',
        'Supervised Learning',
        'TLoL',
        'Dataset Generation',
        'Data Scraping'
    ],
    url='https://github.com/hanueluni1106/pyLoL.git',
    packages=[
        'autoLeague',
        'autoLeague.bin',
        'autoLeague.replays',
        'autoLeague.dataset',
        'autoLeague.preprocess'
    ],
    install_requires=[
        'absl-py',
        'requests',
        'psutil'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ]
)
