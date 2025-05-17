import asyncio
import platform
import subprocess

from config import local_dir, the_doc_log_file_name


async def open_port_on_local(port: int) -> None:
    _pid = await is_port_open(port)
    pid = _pid if isinstance(_pid, str) else None
    if pid:
        await kill_process_on_port(pid)
    else:
        print(f"Port {port} is open to use")


async def is_port_open(port: int):
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


async def kill_process_on_port(pid: str):
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


def run_sync_command(command: str) -> str:
    """
    Synchronous function that uses subprocess.run to execute a shell command.
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout if result.stdout else result.stderr


async def run_command_async(command: str) -> str:
    """
    Asynchronous wrapper that calls the synchronous function in the default ThreadPoolExecutor.
    """
    # await asyncio.to_thread(run_sync_command, command, None) # alternative (TODO: test)
    loop = asyncio.get_running_loop()
    output = await loop.run_in_executor(None, run_sync_command, command)
    return output


async def run_a_command_on_local(command: str) -> str:
    try:
        print(f"Executing [{command}] on local machine")
        return await run_command_async(command)
    except Exception as e:
        raise e
    
def create_command(options: dict) -> str:
    env = options.get("environment")
    app = options.get("app")
    proto = options.get("proto")
    suite = options.get("suite")
    record = options.get("record", "false") # used by Artillery perf tests
    logger = options.get("logger", the_doc_log_file_name)
    os = platform.system().lower()

    if os == "darwin" or os == "linux":
        return f"cd {local_dir} && ENVIRONMENT={env} APP={app} RECORD={record} npm run {proto}:{suite} >> logs/{logger}"
    elif os == "windows":
        return f"cd {local_dir} && set ENVIRONMENT={env}& set APP={app}& set RECORD={record}& npm run {proto}:{suite} >> logs/{logger}"
    else:
        raise OSError("Unsupported OS to run command")
