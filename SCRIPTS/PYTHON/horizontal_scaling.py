"""
Horizontal Scaling Implementation for AUGGDASH26 Dashboard System
This module implements horizontal scaling capabilities for the
AUGGDASH26 dashboard system to handle increased load by adding
more server instances.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import threading
import queue
from enum import Enum

class ScalingStrategy(Enum):
    """Types of scaling strategies"""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    REQUEST_BASED = "request_based"
    CUSTOM_METRIC = "custom_metric"

class ServerStatus(Enum):
    """Status of server instances"""
    PENDING = "pending"
    RUNNING = "running"
    UNHEALTHY = "unhealthy"
    TERMINATING = "terminating"
    TERMINATED = "terminated"

@dataclass
class ServerInstance:
    """Data class for server instances"""
    id: str
    ip_address: str
    status: ServerStatus
    cpu_usage: float
    memory_usage: float
    request_count: int
    start_time: datetime
    health_check_passed: bool = True

@dataclass
class ScalingConfig:
    """Configuration for horizontal scaling"""
    min_instances: int
    max_instances: int
    target_cpu: float  # percentage
    target_memory: float  # percentage
    target_requests_per_second: int
    scale_up_threshold: float  # percentage of target before scaling up
    scale_down_threshold: float  # percentage of target before scaling down
    cooldown_period: int  # seconds
    health_check_interval: int  # seconds

class LoadBalancer:
    """Load balancer to distribute requests across instances"""
    
    def __init__(self):
        self.instances = []
        self.request_counts = {}
        self.current_instance_index = 0
        self.lock = threading.Lock()
    
    def add_instance(self, instance: ServerInstance):
        """Add a server instance to the load balancer"""
        with self.lock:
            self.instances.append(instance)
            self.request_counts[instance.id] = 0
    
    def remove_instance(self, instance_id: str):
        """Remove a server instance from the load balancer"""
        with self.lock:
            self.instances = [inst for inst in self.instances if inst.id != instance_id]
            if instance_id in self.request_counts:
                del self.request_counts[instance_id]
    
    def get_next_instance(self) -> Optional[ServerInstance]:
        """Get the next instance using round-robin algorithm"""
        with self.lock:
            if not self.instances:
                return None
            
            # Filter healthy instances
            healthy_instances = [inst for inst in self.instances if inst.health_check_passed and inst.status == ServerStatus.RUNNING]
            
            if not healthy_instances:
                return None
            
            # Round-robin selection
            instance = healthy_instances[self.current_instance_index % len(healthy_instances)]
            self.current_instance_index = (self.current_instance_index + 1) % len(healthy_instances)
            
            # Increment request count
            self.request_counts[instance.id] += 1
            instance.request_count = self.request_counts[instance.id]
            
            return instance
    
    def update_instance_health(self, instance_id: str, health_status: bool):
        """Update the health status of an instance"""
        with self.lock:
            for instance in self.instances:
                if instance.id == instance_id:
                    instance.health_check_passed = health_status
                    break

class MetricsCollector:
    """Collect metrics for scaling decisions"""
    
    def __init__(self):
        self.metrics_history = []
        self.current_metrics = {}
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system metrics from all instances"""
        # In a real implementation, this would collect actual metrics from all instances
        # For simulation, we'll generate realistic metrics
        
        metrics = {
            'avg_cpu_usage': random.uniform(20, 80),
            'avg_memory_usage': random.uniform(30, 70),
            'total_requests_per_second': random.randint(100, 1000),
            'active_instances': 3,
            'response_time_avg': random.uniform(50, 500),
            'error_rate': random.uniform(0.01, 2.0)
        }
        
        # Store in history
        self.current_metrics = metrics
        self.metrics_history.append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })
        
        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    def get_historical_metrics(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get historical metrics for the specified time period"""
        threshold_time = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics_history if m['timestamp'] >= threshold_time]

class AutoScaler:
    """Main auto-scaling engine"""
    
    def __init__(self, config: ScalingConfig, load_balancer: LoadBalancer, metrics_collector: MetricsCollector):
        self.config = config
        self.load_balancer = load_balancer
        self.metrics_collector = metrics_collector
        self.current_instances = config.min_instances
        self.last_scaling_action = datetime.min
        self.scaling_history = []
        self.scaling_lock = threading.Lock()
        
        # Initialize with minimum instances
        self._initialize_instances()
    
    def _initialize_instances(self):
        """Initialize with minimum number of instances"""
        for i in range(self.config.min_instances):
            instance = self._create_instance(f"instance-{i:03d}")
            self.load_balancer.add_instance(instance)
    
    def _create_instance(self, instance_id: str) -> ServerInstance:
        """Create a new server instance"""
        return ServerInstance(
            id=instance_id,
            ip_address=f"10.0.1.{random.randint(10, 200)}",
            status=ServerStatus.RUNNING,
            cpu_usage=random.uniform(10, 30),
            memory_usage=random.uniform(20, 40),
            request_count=0,
            start_time=datetime.now()
        )
    
    def _terminate_instance(self, instance_id: str):
        """Terminate a server instance"""
        self.load_balancer.remove_instance(instance_id)
    
    def should_scale_up(self, metrics: Dict[str, float]) -> bool:
        """Determine if we should scale up"""
        # Check if we're at max capacity
        if self.current_instances >= self.config.max_instances:
            return False
        
        # Check cooldown period
        time_since_last_action = datetime.now() - self.last_scaling_action
        if time_since_last_action < timedelta(seconds=self.config.cooldown_period):
            return False
        
        # Check if any metric exceeds the scale-up threshold
        cpu_threshold = self.config.target_cpu * (self.config.scale_up_threshold / 100)
        memory_threshold = self.config.target_memory * (self.config.scale_up_threshold / 100)
        rps_threshold = self.config.target_requests_per_second * (self.config.scale_up_threshold / 100)
        
        return (
            metrics['avg_cpu_usage'] > cpu_threshold or
            metrics['avg_memory_usage'] > memory_threshold or
            metrics['total_requests_per_second'] > rps_threshold
        )
    
    def should_scale_down(self, metrics: Dict[str, float]) -> bool:
        """Determine if we should scale down"""
        # Check if we're at min capacity
        if self.current_instances <= self.config.min_instances:
            return False
        
        # Check cooldown period
        time_since_last_action = datetime.now() - self.last_scaling_action
        if time_since_last_action < timedelta(seconds=self.config.cooldown_period):
            return False
        
        # Check if all metrics are below the scale-down threshold
        cpu_threshold = self.config.target_cpu * (self.config.scale_down_threshold / 100)
        memory_threshold = self.config.target_memory * (self.config.scale_down_threshold / 100)
        rps_threshold = self.config.target_requests_per_second * (self.config.scale_down_threshold / 100)
        
        return (
            metrics['avg_cpu_usage'] < cpu_threshold and
            metrics['avg_memory_usage'] < memory_threshold and
            metrics['total_requests_per_second'] < rps_threshold
        )
    
    def scale_up(self):
        """Scale up by adding a new instance"""
        with self.scaling_lock:
            if self.current_instances < self.config.max_instances:
                new_instance_id = f"instance-{self.current_instances:03d}"
                new_instance = self._create_instance(new_instance_id)
                self.load_balancer.add_instance(new_instance)
                
                self.current_instances += 1
                self.last_scaling_action = datetime.now()
                
                scaling_event = {
                    'timestamp': datetime.now(),
                    'action': 'scale_up',
                    'from_instances': self.current_instances - 1,
                    'to_instances': self.current_instances,
                    'reason': 'Metrics exceeded threshold'
                }
                self.scaling_history.append(scaling_event)
                
                print(f"Scaling up: {self.current_instances - 1} -> {self.current_instances} instances")
                return True
        return False
    
    def scale_down(self):
        """Scale down by removing an instance"""
        with self.scaling_lock:
            if self.current_instances > self.config.min_instances:
                # Find an instance with the least requests
                instances = self.load_balancer.instances
                if instances:
                    # Find instance with lowest request count
                    instance_to_remove = min(
                        [inst for inst in instances if inst.status == ServerStatus.RUNNING],
                        key=lambda x: x.request_count,
                        default=None
                    )
                    
                    if instance_to_remove:
                        self._terminate_instance(instance_to_remove.id)
                        
                        self.current_instances -= 1
                        self.last_scaling_action = datetime.now()
                        
                        scaling_event = {
                            'timestamp': datetime.now(),
                            'action': 'scale_down',
                            'from_instances': self.current_instances + 1,
                            'to_instances': self.current_instances,
                            'reason': 'Metrics below threshold'
                        }
                        self.scaling_history.append(scaling_event)
                        
                        print(f"Scaling down: {self.current_instances + 1} -> {self.current_instances} instances")
                        return True
        return False
    
    def make_scaling_decision(self):
        """Make a scaling decision based on current metrics"""
        metrics = self.metrics_collector.collect_system_metrics()
        
        if self.should_scale_up(metrics):
            self.scale_up()
        elif self.should_scale_down(metrics):
            self.scale_down()
        
        return metrics

class HealthChecker:
    """Health checker for instances"""
    
    def __init__(self, load_balancer: LoadBalancer, check_interval: int = 30):
        self.load_balancer = load_balancer
        self.check_interval = check_interval
        self.running = False
        self.health_thread = None
    
    def start(self):
        """Start the health checker"""
        self.running = True
        self.health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_thread.start()
    
    def stop(self):
        """Stop the health checker"""
        self.running = False
        if self.health_thread:
            self.health_thread.join()
    
    def _health_check_loop(self):
        """Main health check loop"""
        while self.running:
            self._perform_health_checks()
            time.sleep(self.check_interval)
    
    def _perform_health_checks(self):
        """Perform health checks on all instances"""
        for instance in self.load_balancer.instances:
            # Simulate health check
            # In a real implementation, this would make actual health check requests
            is_healthy = self._check_instance_health(instance)
            self.load_balancer.update_instance_health(instance.id, is_healthy)
            
            if not is_healthy and instance.status == ServerStatus.RUNNING:
                print(f"Instance {instance.id} is unhealthy")
                # In a real system, we might want to remove unhealthy instances
    
    def _check_instance_health(self, instance: ServerInstance) -> bool:
        """Check the health of a specific instance"""
        # Simulate health check - in reality, this would make an HTTP request to a health endpoint
        # For simulation, we'll randomly mark some instances as unhealthy occasionally
        if instance.status != ServerStatus.RUNNING:
            return False
        
        # Simulate occasional failures
        return random.random() > 0.05  # 95% healthy rate

class ScalingDashboard:
    """Dashboard to monitor scaling activities"""
    
    def __init__(self, auto_scaler: AutoScaler, metrics_collector: MetricsCollector):
        self.auto_scaler = auto_scaler
        self.metrics_collector = metrics_collector
    
    def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status"""
        current_metrics = self.metrics_collector.current_metrics
        return {
            'current_instances': self.auto_scaler.current_instances,
            'min_instances': self.auto_scaler.config.min_instances,
            'max_instances': self.auto_scaler.config.max_instances,
            'current_metrics': current_metrics,
            'scaling_history': self.auto_scaler.scaling_history[-10:],  # Last 10 scaling events
            'last_scaling_action': self.auto_scaler.last_scaling_action.isoformat() if self.auto_scaler.last_scaling_action != datetime.min else None
        }
    
    def get_scaling_recommendation(self) -> str:
        """Get scaling recommendation based on current metrics"""
        metrics = self.metrics_collector.current_metrics
        
        if not metrics:
            return "Waiting for metrics..."
        
        cpu_pressure = metrics['avg_cpu_usage'] / self.auto_scaler.config.target_cpu
        memory_pressure = metrics['avg_memory_usage'] / self.auto_scaler.config.target_memory
        rps_pressure = metrics['total_requests_per_second'] / self.auto_scaler.config.target_requests_per_second
        
        max_pressure = max(cpu_pressure, memory_pressure, rps_pressure)
        
        if max_pressure > 1.2:
            return f"Scale up recommended (pressure: {max_pressure:.2f}x)"
        elif max_pressure < 0.6:
            return f"Scale down considered (pressure: {max_pressure:.2f}x)"
        else:
            return f"Current scaling level appropriate (pressure: {max_pressure:.2f}x)"

class HorizontalScalingManager:
    """Main manager for horizontal scaling"""
    
    def __init__(self):
        # Default scaling configuration
        self.config = ScalingConfig(
            min_instances=3,
            max_instances=20,
            target_cpu=70.0,  # 70% CPU usage target
            target_memory=75.0,  # 75% memory usage target
            target_requests_per_second=500,
            scale_up_threshold=1.2,  # Scale up at 120% of target
            scale_down_threshold=0.6,  # Scale down at 60% of target
            cooldown_period=300,  # 5 minutes cooldown
            health_check_interval=30  # 30 seconds
        )
        
        self.load_balancer = LoadBalancer()
        self.metrics_collector = MetricsCollector()
        self.auto_scaler = AutoScaler(self.config, self.load_balancer, self.metrics_collector)
        self.health_checker = HealthChecker(self.load_balancer, self.config.health_check_interval)
        self.scaling_dashboard = ScalingDashboard(self.auto_scaler, self.metrics_collector)
        self.scaling_thread = None
        self.running = False
    
    def start_scaling_system(self):
        """Start the horizontal scaling system"""
        print("Starting horizontal scaling system...")
        
        # Start health checker
        self.health_checker.start()
        
        # Start scaling thread
        self.running = True
        self.scaling_thread = threading.Thread(target=self._scaling_loop, daemon=True)
        self.scaling_thread.start()
        
        print(f"Horizontal scaling system started with {self.auto_scaler.current_instances} initial instances")
    
    def stop_scaling_system(self):
        """Stop the horizontal scaling system"""
        print("Stopping horizontal scaling system...")
        self.running = False
        
        if self.scaling_thread:
            self.scaling_thread.join(timeout=5)
        
        self.health_checker.stop()
        print("Horizontal scaling system stopped")
    
    def _scaling_loop(self):
        """Main scaling loop"""
        while self.running:
            try:
                # Make scaling decision
                metrics = self.auto_scaler.make_scaling_decision()
                
                # Print status periodically
                if random.random() < 0.1:  # Print status about every 10 iterations
                    status = self.scaling_dashboard.get_scaling_status()
                    print(f"Instances: {status['current_instances']}, "
                          f"CPU: {metrics.get('avg_cpu_usage', 0):.1f}%, "
                          f"RPS: {metrics.get('total_requests_per_second', 0):.0f}")
                
                # Sleep before next iteration
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Error in scaling loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scaling status"""
        return self.scaling_dashboard.get_scaling_status()
    
    def get_recommendation(self) -> str:
        """Get scaling recommendation"""
        return self.scaling_dashboard.get_scaling_recommendation()
    
    def update_scaling_config(self, new_config: ScalingConfig):
        """Update scaling configuration"""
        self.config = new_config
        self.auto_scaler.config = new_config
        self.health_checker.check_interval = new_config.health_check_interval

# Example usage and simulation
def simulate_scaling_scenario():
    """Simulate a scaling scenario"""
    print("Starting horizontal scaling simulation for AUGGDASH26 Dashboard System")
    
    # Initialize scaling manager
    scaling_manager = HorizontalScalingManager()
    
    # Start the scaling system
    scaling_manager.start_scaling_system()
    
    # Simulate different load patterns over time
    print("\nSimulating load patterns...")
    
    # Initial state
    initial_status = scaling_manager.get_status()
    print(f"Initial state: {initial_status['current_instances']} instances")
    
    # Simulate increasing load
    print("\nSimulating increasing load (will trigger scale-up)...")
    for i in range(5):
        time.sleep(2)  # Wait for scaling decision
        status = scaling_manager.get_status()
        print(f"Step {i+1}: {status['current_instances']} instances - {scaling_manager.get_recommendation()}")
    
    # Simulate decreasing load
    print("\nSimulating decreasing load (may trigger scale-down after cooldown)...")
    for i in range(5):
        time.sleep(2)  # Wait for scaling decision
        status = scaling_manager.get_status()
        print(f"Step {i+1}: {status['current_instances']} instances - {scaling_manager.get_recommendation()}")
    
    # Get final status
    final_status = scaling_manager.get_status()
    print(f"\nFinal state: {final_status['current_instances']} instances")
    
    # Show scaling history
    print(f"\nScaling history ({len(final_status['scaling_history'])} events):")
    for event in final_status['scaling_history']:
        print(f"  {event['timestamp'].strftime('%H:%M:%S')} - {event['action'].upper()}: "
              f"{event['from_instances']} -> {event['to_instances']} instances")
    
    # Stop the scaling system
    scaling_manager.stop_scaling_system()
    
    print("\nHorizontal scaling simulation completed!")

# Configuration management
class ScalingConfigManager:
    """Manage scaling configurations"""
    
    def __init__(self):
        self.configs = {}
    
    def create_config(self, name: str, config: ScalingConfig) -> str:
        """Create a new scaling configuration"""
        self.configs[name] = config
        return name
    
    def get_config(self, name: str) -> Optional[ScalingConfig]:
        """Get a scaling configuration by name"""
        return self.configs.get(name)
    
    def list_configs(self) -> List[str]:
        """List all configuration names"""
        return list(self.configs.keys())
    
    def update_config(self, name: str, **kwargs) -> bool:
        """Update an existing configuration"""
        if name not in self.configs:
            return False
        
        config = self.configs[name]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return True
    
    def save_configs_to_file(self, filename: str):
        """Save configurations to a file"""
        config_data = {}
        for name, config in self.configs.items():
            config_data[name] = {
                'min_instances': config.min_instances,
                'max_instances': config.max_instances,
                'target_cpu': config.target_cpu,
                'target_memory': config.target_memory,
                'target_requests_per_second': config.target_requests_per_second,
                'scale_up_threshold': config.scale_up_threshold,
                'scale_down_threshold': config.scale_down_threshold,
                'cooldown_period': config.cooldown_period,
                'health_check_interval': config.health_check_interval
            }
        
        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2, default=str)
    
    def load_configs_from_file(self, filename: str):
        """Load configurations from a file"""
        with open(filename, 'r') as f:
            config_data = json.load(f)
        
        for name, data in config_data.items():
            config = ScalingConfig(**data)
            self.configs[name] = config

if __name__ == "__main__":
    # Run the scaling simulation
    simulate_scaling_scenario()
    
    # Create and save a configuration
    config_manager = ScalingConfigManager()
    
    # Create a production configuration
    prod_config = ScalingConfig(
        min_instances=5,
        max_instances=50,
        target_cpu=65.0,
        target_memory=70.0,
        target_requests_per_second=1000,
        scale_up_threshold=1.3,
        scale_down_threshold=0.5,
        cooldown_period=300,
        health_check_interval=15
    )
    
    config_manager.create_config("production", prod_config)
    
    # Create a development configuration
    dev_config = ScalingConfig(
        min_instances=2,
        max_instances=10,
        target_cpu=80.0,
        target_memory=85.0,
        target_requests_per_second=200,
        scale_up_threshold=1.5,
        scale_down_threshold=0.4,
        cooldown_period=120,
        health_check_interval=30
    )
    
    config_manager.create_config("development", dev_config)
    
    # Save configurations to file
    config_manager.save_configs_to_file("scaling_configs.json")
    print("\nScaling configurations saved to 'scaling_configs.json'")
    
    print("\nHorizontal scaling capabilities implemented successfully!")
    print("Features included:")
    print("- Auto-scaling based on CPU, memory, and request metrics")
    print("- Load balancing with health checks")
    print("- Configurable scaling policies")
    print("- Scaling dashboard and monitoring")
    print("- Configuration management")