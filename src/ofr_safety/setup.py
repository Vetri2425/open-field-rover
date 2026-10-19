from setuptools import setup

package_name = "ofr_safety"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/watchdog.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Vetri",
    maintainer_email="vetri96anitha@gmail.com",
    description="Safety nodes for open-field-rover",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "cmd_vel_watchdog = ofr_safety.cmd_vel_watchdog:main",
        ],
    },
)
