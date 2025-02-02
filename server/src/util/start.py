import os
import platform
import subprocess


def main():
  os_name = platform.system()
  print(os_name)

  if os_name == "Windows":
    os.environ["OS_NAME"] = "Windows"
  elif os_name == "Darwin":
    os.environ["OS_NAME"] = "Mac"
  elif os_name == "Linux":
    os.environ["OS_NAME"] = "Linux"
  else:
    print("Unknown OS")

  subprocess.run(["sh", "./start.sh"])


if __name__ == "__main__":
  main()
