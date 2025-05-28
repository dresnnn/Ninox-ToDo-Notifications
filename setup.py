from setuptools import setup, find_packages

setup(
    name="ninox_notification",
    version="0.1.0",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'requests',
        'PyYAML',
        'schedule',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'ninox-notify=ninox_notification.notify:cli',
            'ninox-notify-service=ninox_notification.service:cli',
        ]
    },
)
