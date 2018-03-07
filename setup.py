from setuptools import setup, find_packages
from codecs import open
from os import path

workdir = path.abspath(path.dirname(__file__))

with open(path.join(workdir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name='SSHX11VNCTunnel',
        version='0.0.1a',
        description='A gui for launching m y remote desktop.',
        long_description=long_description,
        url='https://github.com/mskymoore/SSHX11VNCTunnel',
        author='Sky Moore',
        author_email='mskymoore@gmail.com',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Linux Users',
            'Topic :: Remote Desktop',
            'License :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
        keywords='VNC X11 SSH',
        packages=find_packages(exclude=['tests']),
        package_data={
            'SSHX11VNCTunnel': ['S2.png', 'ssh_kill_vnc.sh', 'ssh_vnc.sh'],
        },
        entry_points={
            'console_scripts': [ 
                'SSHX11VNCTunnel=SSHX11VNCTunnel:Main',
            ],
        },
     )
