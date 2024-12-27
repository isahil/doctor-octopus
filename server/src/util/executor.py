import asyncio
import platform
import subprocess

async def is_port_open(port):
    try:
        os = platform.system().lower()
        print(f"Checking if port {port} is open on {os}")
        if os == "darwin" or os == "linux":
            result = await run_a_command_on_local(f"lsof -ti:{port}")
            return result
    except OSError as e:
        return e

async def kill_process_on_port(pid):
    try:
        os = platform.system().lower()
        print(f"Killing process on port {pid} on {os}")
        if os == "darwin" or os == "linux":
            await run_a_command_on_local(f"kill -9 {pid}")

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
        print(f"Executing command on local: {command}")
        task = asyncio.create_task(run_command_async(command))
        output = await task
        print(f"Command output executed on local: {output}")
        return output
    except Exception as e:
        raise e
