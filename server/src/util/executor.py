import asyncio
import platform
import subprocess

async def is_port_open(port):
    try:
        os = platform.system().lower()
        print(f"Checking if port {port} is open on {os} machine")

        if os == "darwin" or os == "linux":
            command = f"lsof -ti:{port}"
            pid = await run_a_command_on_local(command)
        if os == "windows":
            # command = f'Get-NetTCPConnection -LocalPort {port} | Select-Object -ExpandProperty OwningProcess'
            command = f'netstat -aon | findstr :{port} | findstr LISTENING'
            result = await run_a_command_on_local(command)
            pid = result.split()[-1] if len(result) > 0 else result
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
        else: command = f"taskkill /PID {pid} /F"
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
        print(f"Executing command on local: {command}")
        task = asyncio.create_task(run_command_async(command))
        output = await task
        print(f"Command output executed on local: {output}")
        return output
    except Exception as e:
        raise e
