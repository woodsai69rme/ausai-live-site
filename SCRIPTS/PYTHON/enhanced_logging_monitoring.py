"""
Enhanced Logging and Monitoring Module for YouTube Enhancement Tools
This module provides enhanced logging, monitoring, and performance tracking capabilities.
"""

import logging
import logging.handlers
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import psutil
import threading
import queue
from dataclasses import dataclass, asdict
from enum import Enum
import atexit


class LogLevel(Enum):
    """Enumeration for log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Data class for log entries"""
    timestamp: datetime
    level: str
    module: str
    message: str
    extra_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class PerformanceMonitor:
    """Class to monitor system and application performance"""
    
    def __init__(self, log_interval: int = 30):
        self.log_interval = log_interval  # seconds
        self.process = psutil.Process()
        self.monitoring = False
        self.monitor_thread = None
        self.performance_log = []
        self.max_log_entries = 1000  # Keep only last 1000 entries
    
    def start_monitoring(self):
        """Start performance monitoring in a separate thread"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Collect performance metrics
                metrics = self._collect_metrics()
                
                # Add to performance log
                self.performance_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'metrics': metrics
                })
                
                # Trim log if too long
                if len(self.performance_log) > self.max_log_entries:
                    self.performance_log = self.performance_log[-self.max_log_entries:]
                
                # Sleep for the specified interval
                time.sleep(self.log_interval)
                
            except Exception as e:
                print(f"Error in performance monitoring: {e}")
                time.sleep(self.log_interval)
    
    def _collect_metrics(self) -> Dict[str, float]:
        """Collect current system metrics"""
        try:
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
            disk_usage = psutil.disk_usage('.').percent
            network_io = psutil.net_io_counters()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_mb,
                'memory_percent': self.process.memory_percent(),
                'disk_percent': disk_usage,
                'network_bytes_sent': network_io.bytes_sent,
                'network_bytes_recv': network_io.bytes_recv,
                'num_threads': self.process.num_threads(),
                'num_fds': self.process.num_fds() if hasattr(self.process, 'num_fds') else 0,
            }
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return {}
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        return self._collect_metrics()
    
    def get_performance_history(self, minutes: int = 10) -> List[Dict]:
        """Get performance history for the last N minutes"""
        cutoff_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        return [entry for entry in self.performance_log if entry['timestamp'] >= cutoff_time]
    
    def get_average_metrics(self, minutes: int = 10) -> Dict[str, float]:
        """Get average metrics over the last N minutes"""
        history = self.get_performance_history(minutes)
        if not history:
            return {}
        
        # Calculate averages
        avg_metrics = {}
        metric_keys = history[0]['metrics'].keys()
        
        for key in metric_keys:
            values = [entry['metrics'][key] for entry in history if key in entry['metrics']]
            if values:
                avg_metrics[f"avg_{key}"] = sum(values) / len(values)
        
        return avg_metrics


class AdvancedLogger:
    """Advanced logging class with multiple handlers and performance tracking"""
    
    def __init__(self, log_file: str = "youtube_enhancement_tools_advanced.log", 
                 max_file_size: int = 10 * 1024 * 1024,  # 10 MB
                 backup_count: int = 5):
        self.logger = logging.getLogger('YouTubeEnhancementTools')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Queue for async logging
        self.log_queue = queue.Queue()
        self.async_handler = None
        self.async_thread = None
        self.async_logging = False
    
    def start_async_logging(self):
        """Start asynchronous logging to improve performance"""
        if self.async_logging:
            return
        
        self.async_logging = True
        
        # Create a queue handler
        from logging.handlers import QueueHandler, QueueListener
        
        self.async_handler = QueueHandler(self.log_queue)
        self.logger.addHandler(self.async_handler)
        
        # Create listener thread
        self.async_listener = QueueListener(
            self.log_queue, 
            *(handler for handler in self.logger.handlers if not isinstance(handler, QueueHandler))
        )
        self.async_listener.start()
    
    def stop_async_logging(self):
        """Stop asynchronous logging"""
        if self.async_logging and self.async_listener:
            self.async_listener.stop()
            self.async_logging = False
    
    def log(self, level: LogLevel, module: str, message: str, extra_data: Optional[Dict] = None):
        """Log a message with additional metadata"""
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level.value,
            module=module,
            message=message,
            extra_data=extra_data
        )
        
        # Log to standard logger
        log_method = getattr(self.logger, level.value.lower())
        log_method(f"[{module}] {message}", extra={'extra_data': extra_data})
    
    def debug(self, module: str, message: str, extra_data: Optional[Dict] = None):
        """Log debug message"""
        self.log(LogLevel.DEBUG, module, message, extra_data)
    
    def info(self, module: str, message: str, extra_data: Optional[Dict] = None):
        """Log info message"""
        self.log(LogLevel.INFO, module, message, extra_data)
    
    def warning(self, module: str, message: str, extra_data: Optional[Dict] = None):
        """Log warning message"""
        self.log(LogLevel.WARNING, module, message, extra_data)
    
    def error(self, module: str, message: str, extra_data: Optional[Dict] = None):
        """Log error message"""
        self.log(LogLevel.ERROR, module, message, extra_data)
    
    def critical(self, module: str, message: str, extra_data: Optional[Dict] = None):
        """Log critical message"""
        self.log(LogLevel.CRITICAL, module, message, extra_data)


class OperationTracker:
    """Track operations and their performance"""
    
    def __init__(self):
        self.operations = {}
        self.lock = threading.Lock()
    
    def start_operation(self, op_id: str, op_name: str, metadata: Optional[Dict] = None):
        """Start tracking an operation"""
        with self.lock:
            self.operations[op_id] = {
                'name': op_name,
                'start_time': time.time(),
                'metadata': metadata or {},
                'status': 'running'
            }
    
    def end_operation(self, op_id: str, success: bool = True, result: Optional[Any] = None):
        """End tracking an operation"""
        with self.lock:
            if op_id in self.operations:
                op = self.operations[op_id]
                op['end_time'] = time.time()
                op['duration'] = op['end_time'] - op['start_time']
                op['success'] = success
                op['result'] = result
                op['status'] = 'completed' if success else 'failed'
                
                return op['duration']
        return None
    
    def get_operation_stats(self) -> Dict[str, Any]:
        """Get statistics about operations"""
        with self.lock:
            completed_ops = [op for op in self.operations.values() if op.get('duration')]
            
            if not completed_ops:
                return {
                    'total_operations': len(self.operations),
                    'completed_operations': 0,
                    'average_duration': 0,
                    'success_rate': 0
                }
            
            total_duration = sum(op['duration'] for op in completed_ops)
            successful_ops = [op for op in completed_ops if op['success']]
            
            return {
                'total_operations': len(self.operations),
                'completed_operations': len(completed_ops),
                'successful_operations': len(successful_ops),
                'failed_operations': len(completed_ops) - len(successful_ops),
                'average_duration': total_duration / len(completed_ops),
                'success_rate': len(successful_ops) / len(completed_ops) if completed_ops else 0
            }
    
    def get_slow_operations(self, threshold: float = 5.0) -> List[Dict]:
        """Get operations that took longer than the threshold"""
        with self.lock:
            slow_ops = []
            for op in self.operations.values():
                if op.get('duration', 0) > threshold:
                    slow_ops.append(op)
            return slow_ops


class SystemHealthMonitor:
    """Monitor overall system health"""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread = None
        self.health_log = []
        self.max_health_entries = 100
    
    def start_monitoring(self):
        """Start health monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.monitor_thread.start()
        print("System health monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("System health monitoring stopped")
    
    def _health_check_loop(self):
        """Main health check loop"""
        while self.monitoring:
            try:
                health_status = self._check_system_health()
                
                # Add to health log
                self.health_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'status': health_status
                })
                
                # Trim log if too long
                if len(self.health_log) > self.max_health_entries:
                    self.health_log = self.health_log[-self.max_health_entries:]
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Error in health monitoring: {e}")
                time.sleep(self.check_interval)
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check system health"""
        try:
            # Overall system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process-specific stats
            process = psutil.Process()
            proc_cpu = process.cpu_percent()
            proc_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            health_status = {
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                    'healthy': cpu_percent < 80 and memory.percent < 80 and disk.percent < 90
                },
                'application': {
                    'cpu_percent': proc_cpu,
                    'memory_mb': proc_memory,
                    'healthy': proc_cpu < 70 and proc_memory < 1000  # Less than 1GB
                }
            }
            
            # Determine overall health
            overall_healthy = (
                health_status['system']['healthy'] and 
                health_status['application']['healthy']
            )
            health_status['overall_healthy'] = overall_healthy
            health_status['timestamp'] = datetime.now().isoformat()
            
            return health_status
            
        except Exception as e:
            print(f"Error checking system health: {e}")
            return {
                'error': str(e),
                'overall_healthy': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def is_system_healthy(self) -> bool:
        """Check if the system is currently healthy"""
        health_status = self._check_system_health()
        return health_status.get('overall_healthy', False)


# Global instances
advanced_logger = AdvancedLogger()
performance_monitor = PerformanceMonitor()
operation_tracker = OperationTracker()
system_health_monitor = SystemHealthMonitor()


def setup_enhanced_monitoring():
    """Setup enhanced logging and monitoring for the application"""
    # Start all monitoring components
    performance_monitor.start_monitoring()
    system_health_monitor.start_monitoring()
    advanced_logger.start_async_logging()
    
    # Register cleanup function
    def cleanup():
        performance_monitor.stop_monitoring()
        system_health_monitor.stop_monitoring()
        advanced_logger.stop_async_logging()
    
    atexit.register(cleanup)
    
    print("Enhanced monitoring setup completed")


def log_application_event(event_type: str, message: str, data: Optional[Dict] = None):
    """Log an application event with enhanced logging"""
    advanced_logger.info(
        module="Application",
        message=f"{event_type}: {message}",
        extra_data=data
    )


def track_operation(op_name: str, func, *args, **kwargs):
    """Execute a function with operation tracking"""
    op_id = f"{op_name}_{int(time.time() * 1000000)}"
    operation_tracker.start_operation(op_id, op_name, {
        'args': str(args)[:100],  # Limit length
        'kwargs_keys': list(kwargs.keys())
    })
    
    try:
        result = func(*args, **kwargs)
        duration = operation_tracker.end_operation(op_id, success=True, result=result)
        advanced_logger.info(
            module="OperationTracker",
            message=f"Completed {op_name} in {duration:.2f}s",
            extra_data={'operation_id': op_id, 'duration': duration}
        )
        return result
    except Exception as e:
        duration = operation_tracker.end_operation(op_id, success=False, result=str(e))
        advanced_logger.error(
            module="OperationTracker",
            message=f"Failed {op_name} after {duration:.2f}s: {e}",
            extra_data={'operation_id': op_id, 'duration': duration, 'error': str(e)}
        )
        raise


if __name__ == "__main__":
    # Example usage of enhanced logging and monitoring
    print("YouTube Enhancement Tools - Enhanced Logging and Monitoring")
    print("=" * 60)
    
    # Setup enhanced monitoring
    setup_enhanced_monitoring()
    
    # Log some events
    log_application_event("STARTUP", "Application started successfully")
    log_application_event("CONFIG_LOAD", "Configuration loaded", {"config_file": "config.json"})
    
    # Simulate some operations
    def sample_operation(x, y):
        time.sleep(0.5)  # Simulate work
        return x + y
    
    # Track an operation
    result = track_operation("sample_calculation", sample_operation, 5, 3)
    print(f"Operation result: {result}")
    
    # Get operation stats
    stats = operation_tracker.get_operation_stats()
    print(f"Operation stats: {stats}")
    
    # Check current performance metrics
    current_metrics = performance_monitor.get_current_metrics()
    print(f"Current performance metrics: {current_metrics}")
    
    # Check system health
    is_healthy = system_health_monitor.is_system_healthy()
    print(f"System health status: {'Healthy' if is_healthy else 'Unhealthy'}")
    
    # Wait a bit to collect some data
    time.sleep(2)
    
    # Get performance history
    history = performance_monitor.get_performance_history(minutes=1)
    print(f"Collected {len(history)} performance data points")
    
    # Get average metrics
    avg_metrics = performance_monitor.get_average_metrics(minutes=1)
    print(f"Average metrics: {avg_metrics}")
    
    print("\nEnhanced logging and monitoring is active!")
    print("Press Ctrl+C to stop...")
    
    try:
        # Keep running to demonstrate monitoring
        while True:
            time.sleep(10)
            # Periodically log system status
            current_metrics = performance_monitor.get_current_metrics()
            if current_metrics:
                advanced_logger.debug(
                    module="SystemMonitor",
                    message="Periodic system check",
                    extra_data=current_metrics
                )
    except KeyboardInterrupt:
        print("\nStopping enhanced monitoring...")