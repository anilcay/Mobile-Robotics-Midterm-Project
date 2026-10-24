from setuptools import find_packages, setup

package_name = 'serabot_sensors'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='anilcay',
    maintainer_email='ahmetanilcay@ogr.iuc.edu.tr',
    description='Sensor helper nodes for SeraBot (camera color detector, IMU monitor).',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    # Entry points are registered up front so module owners never edit this
    # file at the same time. Each module must provide a main() function.
    entry_points={
        'console_scripts': [
            # Owner: Member B (camera)
            'color_detector = serabot_sensors.color_detector:main',
            # Owner: shared (IMU)
            'imu_monitor = serabot_sensors.imu_monitor:main',
        ],
    },
)
