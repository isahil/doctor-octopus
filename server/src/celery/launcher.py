import argparse
from src.celery.app import celery_app


def launch_services(services=None, init=True, wait_for_result=True):
    """
    Launch services using Celery tasks
    Args:
        services (list): List of services to launch. Default is ["main"]
        init (bool): Whether to run initialization first. Default is True
        wait_for_result (bool): Whether to wait for task results. Default is True
    Returns:
        dict: Results of launched tasks
    """
    if services is None:
        services = ["main"]

    results = {}

    # Run initialization if requested
    if init:
        print("Running environment initialization...")
        init_task = celery_app.send_task("src.celery.tasks.initialize_environment")

        if wait_for_result:
            init_result = init_task.get(timeout=60)  # Wait up to 60 seconds
            print(f"Initialization result: {init_result}")
            results["init"] = init_result

    # Map service names to tasks
    task_mapping = {
        "main": "src.celery.tasks.run_main_server",
        "notification": "src.celery.tasks.run_notification_server",
    }

    # Launch requested services
    for service in services:
        print(f"Launching {service} service...")
        if service in task_mapping:
            # print(f"Launching {service} service...")
            task = celery_app.send_task(task_mapping[service])

            if wait_for_result:
                try:
                    task_result = task.get(timeout=30)  # Wait up to 30 seconds for server to start
                    results[service] = task_result
                    print(f"{service} service result: {task_result}")
                except Exception as e:
                    print(f"Error starting {service} service: {e}")
                    results[service] = {"status": "error", "message": str(e)}
        else:
            print(f"Unknown service: {service}")

    return results


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Launch Doctor Octopus services")
    parser.add_argument(
        "--services",
        nargs="+",
        default=["main"],
        choices=["main", "notification", "all"],
        help="Services to launch (default: main)",
    )
    parser.add_argument("--no-init", action="store_true", help="Skip environment initialization")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for task results")

    args = parser.parse_args()

    # Process "all" option
    if "all" in args.services:
        services = ["main", "notification"]
    else:
        services = args.services

    # Launch services
    results = launch_services(services=services, init=not args.no_init, wait_for_result=not args.no_wait)

    if not args.no_wait:
        print("\nLaunch Summary:")
        for service, result in results.items():
            print(f"- {service}: {result.get('status', 'unknown')}")

        print("\nServices are now running. To monitor them, visit the Flower dashboard at http://localhost:5555")
        print("To stop all services, run: python src/celery/terminate.py")
    else:
        print("\nServices are being launched in the background.")
        print("Monitor their status using the Flower dashboard at http://localhost:5555")
