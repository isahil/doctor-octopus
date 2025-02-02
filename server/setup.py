from setuptools import setup, find_packages
import platform

app_requires = [
  "aiofiles==24.1.0",
  "annotated-types==0.7.0",
  "anyio==4.4.0",
  "bidict==0.23.1",
  "boto3==1.34.136",
  "botocore==1.34.136",
  "click==8.1.7",
  "fastapi-slim==0.111.0",
  "h11==0.14.0",
  "idna==3.7",
  "jmespath==1.0.1",
  "pydantic==2.7.3",
  "pydantic_core==2.18.4",
  "python-dateutil==2.9.0.post0",
  "python-dotenv==1.0.1",
  "python-engineio==4.9.1",
  "python-socketio==5.11.2",
  "redis==5.2.1",
  "s3transfer==0.10.2",
  "simple-websocket==1.0.0",
  "six==1.16.0",
  "sniffio==1.3.1",
  "starlette==0.37.2",
  "typing_extensions==4.12.2",
  "urllib3<=2.2.2",
  "uvicorn==0.30.1",
  "wsproto==1.2.0",
]

test_requires = []
app_test_requires = app_requires + test_requires

# Define OS-specific dependencies
extras_require = {
  "windows": [],
  "linux": [],
  "macos": [],
  "test": test_requires,
  "app-test": app_requires + test_requires,
}

# Detect the operating system and include the appropriate dependencies
current_os = platform.system().lower()
if current_os == "windows":
  app_requires.extend(extras_require["windows"])
elif current_os == "linux":
  app_requires.extend(extras_require["linux"])
elif current_os == "darwin":
  app_requires.extend(extras_require["macos"])

setup(
  name="doctor-octopus",
  version="1.0.0",
  packages=find_packages(),
  install_requires=app_requires,
  extras_require=extras_require,
)
