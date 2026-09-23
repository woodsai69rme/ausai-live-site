import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { SettingsPage } from './pages/SettingsPage';
import { MCPPage } from './pages/MCPPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { ResearchPage } from './pages/ResearchPage';
import { AccountsBrowserPage } from './pages/AccountsBrowserPage';
import { MainLayout } from './components/layouts/MainLayout';
import { ThemeProvider } from './contexts/ThemeContext';
import { ToastProvider } from './contexts/ToastContext';
import { SettingsProvider, useSettings } from './contexts/SettingsContext';
import { ProjectPage } from './pages/ProjectPage';
import { DisconnectScreenOverlay } from './components/DisconnectScreenOverlay';
import { ErrorBoundaryWithBugReport } from './components/bug-report/ErrorBoundaryWithBugReport';
import { serverHealthService } from './services/serverHealthService';

// 🚀 Archon AI Knowledge OS - Research Intelligence integrated
const AppRoutes = () => {
  const { projectsEnabled } = useSettings();
  
  return (
    <Routes>
      <Route path="/" element={<KnowledgeBasePage />} />
      <Route path="/onboarding" element={<OnboardingPage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="/mcp" element={<MCPPage />} />
      <Route path="/research" element={<ResearchPage />} />
      <Route path="/accounts" element={<AccountsBrowserPage />} />
      {projectsEnabled ? (
        <Route path="/projects" element={<ProjectPage />} />
      ) : (
        <Route path="/projects" element={<Navigate to="/" replace />} />
      )}
    </Routes>
  );
};

const AppContent = () => {
  const [disconnectScreenActive, setDisconnectScreenActive] = useState(false);
  const [disconnectScreenDismissed, setDisconnectScreenDismissed] = useState(false);
  const [disconnectScreenSettings, setDisconnectScreenSettings] = useState({
    enabled: true,
    delay: 10000
  });

  useEffect(() => {
    const settings = serverHealthService.getSettings();
    setDisconnectScreenSettings(settings);
    serverHealthService.stopMonitoring();

    /* Monitoring disabled in offline mode
    serverHealthService.startMonitoring({
      onDisconnected: () => {
        if (!disconnectScreenDismissed) {
          setDisconnectScreenActive(true);
        }
      },
      onReconnected: () => {
        setDisconnectScreenActive(false);
        setDisconnectScreenDismissed(false);
        window.location.reload();
      }
    });
    */

    return () => {
      serverHealthService.stopMonitoring();
    };
  }, [disconnectScreenDismissed]);

  const handleDismissDisconnectScreen = () => {
    setDisconnectScreenActive(false);
    setDisconnectScreenDismissed(true);
  };

  return (
    <>
      <Router>
        <ErrorBoundaryWithBugReport>
          <MainLayout>
            <AppRoutes />
          </MainLayout>
        </ErrorBoundaryWithBugReport>
      </Router>
      <DisconnectScreenOverlay
        isActive={disconnectScreenActive && disconnectScreenSettings.enabled}
        onDismiss={handleDismissDisconnectScreen}
      />
    </>
  );
};

export function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <SettingsProvider>
          <AppContent />
        </SettingsProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}