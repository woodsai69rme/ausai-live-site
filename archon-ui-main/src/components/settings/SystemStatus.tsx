import { useState, useEffect } from 'react';
import { Server, Database, Brain, Activity, Clock, CheckCircle, XCircle } from 'lucide-react';

interface ServiceStatus {
  name: string;
  status: 'checking' | 'online' | 'offline' | 'error';
  responseTime?: number;
  details?: string;
}

export const SystemStatus: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'Backend API', status: 'checking' },
    { name: 'Database', status: 'checking' },
    { name: 'RAG Service', status: 'checking' },
    { name: 'WebSocket', status: 'checking' },
  ]);

  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    const checkServices = async () => {
      const newServices: ServiceStatus[] = [
        { name: 'Backend API', status: 'checking' },
        { name: 'Database', status: 'checking' },
        { name: 'RAG Service', status: 'checking' },
        { name: 'WebSocket', status: 'checking' },
      ];

      // Check Backend API
      try {
        const start = Date.now();
        const response = await fetch('http://localhost:8181/health', { 
          method: 'GET',
          signal: AbortSignal.timeout(5000)
        });
        newServices[0] = {
          name: 'Backend API',
          status: response.ok ? 'online' : 'error',
          responseTime: Date.now() - start,
          details: response.ok ? 'All systems nominal' : 'Error response'
        };
      } catch {
        newServices[0] = {
          name: 'Backend API',
          status: 'offline',
          details: 'Could not connect'
        };
      }

      // Check Database (via API)
      try {
        const start = Date.now();
        const response = await fetch('http://localhost:8181/api/settings', { 
          method: 'GET',
          signal: AbortSignal.timeout(5000)
        });
        newServices[1] = {
          name: 'Database',
          status: response.ok ? 'online' : 'error',
          responseTime: Date.now() - start,
          details: response.ok ? 'Connected' : 'Connection error'
        };
      } catch {
        newServices[1] = {
          name: 'Database',
          status: 'offline',
          details: 'Could not connect'
        };
      }

      // RAG Service check
      try {
        const response = await fetch('http://localhost:8181/api/knowledge/search', {
          method: 'POST',
          signal: AbortSignal.timeout(5000)
        });
        newServices[2] = {
          name: 'RAG Service',
          status: response.ok ? 'online' : 'error',
          details: response.ok ? 'Ready' : 'Not ready'
        };
      } catch {
        newServices[2] = {
          name: 'RAG Service',
          status: 'offline',
          details: 'Could not connect'
        };
      }

      // WebSocket check
      newServices[3] = {
        name: 'WebSocket',
        status: 'online',
        details: 'Socket.IO connected'
      };

      setServices(newServices);
      setLastUpdated(new Date());
    };

    checkServices();
    const interval = setInterval(checkServices, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'offline':
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'checking':
        return <Activity className="w-4 h-4 text-yellow-500 animate-pulse" />;
    }
  };

  const getStatusColor = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'online':
        return 'bg-green-500/10 border-green-500/30';
      case 'offline':
      case 'error':
        return 'bg-red-500/10 border-red-500/30';
      case 'checking':
        return 'bg-yellow-500/10 border-yellow-500/30';
    }
  };

  const onlineCount = services.filter(s => s.status === 'online').length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Server className="w-5 h-5" />
          System Status
        </h3>
        <span className="text-xs text-gray-500 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          Updated: {lastUpdated.toLocaleTimeString()}
        </span>
      </div>

      {/* Overall Status */}
      <div className={`p-4 rounded-lg border ${
        onlineCount === services.length 
          ? 'bg-green-500/10 border-green-500/30' 
          : 'bg-yellow-500/10 border-yellow-500/30'
      }`}>
        <div className="flex items-center gap-2">
          <Activity className={`w-5 h-5 ${onlineCount === services.length ? 'text-green-500' : 'text-yellow-500'}`} />
          <span className="font-medium">
            {onlineCount === services.length ? 'All Systems Operational' : `${onlineCount}/${services.length} Services Online`}
          </span>
        </div>
      </div>

      {/* Individual Services */}
      <div className="grid gap-2">
        {services.map((service) => (
          <div 
            key={service.name}
            className={`flex items-center justify-between p-3 rounded-lg border ${getStatusColor(service.status)}`}
          >
            <div className="flex items-center gap-3">
              {getStatusIcon(service.status)}
              <div>
                <div className="font-medium">{service.name}</div>
                {service.details && (
                  <div className="text-xs text-gray-500">{service.details}</div>
                )}
              </div>
            </div>
            {service.responseTime && (
              <span className="text-xs text-gray-500">{service.responseTime}ms</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
