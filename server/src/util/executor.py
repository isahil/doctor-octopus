import asyncio
import platform
import subprocess

async def open_port_on_local(port):
  pid = await is_port_open(port)
  if pid:
    await kill_process_on_port(pid)
  else:
    print(f"Port {port} is open to use")


async def is_port_open(port):
  """Check if a port is open on the local machine. Return the PID of the process using the port if open"""
  try:
    os = platform.system().lower()
    print(f"Checking if port {port} is open on {os} machine")

    if os == "darwin" or os == "linux":
      command = f"lsof -ti :{port}"
      result = await run_a_command_on_local(command)
    elif os == "windows":
      command = f"netstat -aon | findstr :{port} | findstr LISTENING"
      result = await run_a_command_on_local(command)
    else:
      raise OSError("Unsupported OS to check port")
    pid = result.split()[-1] if result else result
    print(f"PID: {pid}")
    return pid
  except OSError as e:
    return e


async def kill_process_on_port(pid):
  try:
    os = platform.system().lower()
    print(f"Killing process for PID {pid} on {os}")
    if os == "darwin" or os == "linux":
      command = f"kill -9 {pid}"
    elif os == "windows":
      command = f"taskkill /PID {pid} /F"
    else:
      raise OSError("Unsupported OS to kill process")
    await run_a_command_on_local(command)

  except OSError as e:
    return e


def run_sync_command(command: str):
  """
  Synchronous function that uses subprocess.run to execute a shell command.
  """
  result = subprocess.run(command, shell=True, capture_output=True, text=True)
  return result.stdout if result.stdout else result.stderr


async def run_command_async(command: str):
  """
  Asynchronous wrapper that calls the synchronous function in a thread pool.
  """
  loop = asyncio.get_running_loop()
  # Run run_sync_command in the default ThreadPoolExecutor
  output = await loop.run_in_executor(None, run_sync_command, command)
  return output


async def run_a_command_on_local(command):
  try:
    print(f"Executing [{command}] on local machine")
    return await run_command_async(command)
  except Exception as e:
    raise e
