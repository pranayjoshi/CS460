from setuptools import setup
 
package_name = 'hw2'
 
setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Turtlesim shape publishers: circle, rectangle, diamond, random',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # "ros2 run hw2 <name>"  ->  <module>:<function>
            'circle = hw2.circle:main',
            'rectangle = hw2.rectangle:main',
            'diamond = hw2.diamond:main',
            'random = hw2.random:main',
        ],
    },
)
 