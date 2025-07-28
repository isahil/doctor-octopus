import argparse
from src.celery.app import celery_app

def stop_services(services=None):
    """
    Stop specific services or all services.
    Args:
        services (list): List of (service_name, port) tuples to stop
                        If None, stops all services
    """
    if services is None:
        print("Stopping all services...")
        result = celery_app.send_task("src.celery.tasks.stop_all_services")
        try:
            services_stopped = result.get(timeout=10)
            print(f"Services stopped: {services_stopped}")
            return services_stopped
        except Exception as e:
            print(f"Error stopping services: {e}")
            return {"status": "error", "message": str(e)}
    else:
        results = {}
        for service, port in services:
            print(f"Stopping {service} on port {port}...")
            try:
                # task = stop_service.delay(service, port)
                task = celery_app.send_task("src.celery.tasks.stop_service", args=[service, port])
                result = task.get(timeout=10)
                results[f"{service}_{port}"] = result
                print(f"Stop result: {result}")
            except Exception as e:
                print(f"Error stopping {service} on port {port}: {e}")
                results[f"{service}_{port}"] = {"status": "error", "message": str(e)}
        
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stop Doctor Octopus services")
    parser.add_argument(
        "--service", 
        choices=["main", "notification"],
        help="Service to stop"
    )
    parser.add_argument(
        "--port", 
        type=int,
        help="Port of the service to stop"
    )
    
    args = parser.parse_args()
    
    if args.service and args.port:
        stop_services([(args.service, args.port)])
    else:
        stop_services()