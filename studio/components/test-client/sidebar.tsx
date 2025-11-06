/**
 * Sidebar Component - App and Locale Selection
 * 
 * Copyright (c) 2025 Athena Decision Systems
 */

"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useTestClientStore } from "@/lib/store/useTestClientStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, Globe, Server, Loader2, AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";

export function Sidebar() {
  // Collapsed state with localStorage persistence
  const [isCollapsed, setIsCollapsed] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    }
    return false;
  });

  const toggleCollapse = () => {
    setIsCollapsed(prev => {
      const newValue = !prev;
      localStorage.setItem('sidebarCollapsed', String(newValue));
      return newValue;
    });
  };

  const {
    selectedAppId,
    selectedLocale,
    selectedLlmConfigId,
    selectedDecisionEngineConfigId,
    setSelectedApp,
    setSelectedLocale,
    setSelectedLlmConfigId,
    setSelectedDecisionEngineConfigId,
    resetWorkflow,
  } = useTestClientStore();

  // Handle app selection - reset workflow when changing app
  const handleAppSelect = (appId: string) => {
    if (selectedAppId !== appId) {
      resetWorkflow(); // Reset all selections
      setSelectedApp(appId); // Set new app
    }
  };

  // Fetch available apps
  const { data: appIds, isLoading: loadingApps, error: appsError } = useQuery({
    queryKey: ["appIds"],
    queryFn: () => apiClient.getAppIds(),
  });

  // Fetch locales for selected app
  const { data: locales, isLoading: loadingLocales } = useQuery({
    queryKey: ["locales", selectedAppId],
    queryFn: () => apiClient.getLocales(selectedAppId!),
    enabled: !!selectedAppId,
  });

  // Fetch LLM configs for selected app
  const { data: llmConfigs } = useQuery({
    queryKey: ["llmConfigs", selectedAppId],
    queryFn: () => apiClient.getLlmConfigIds(selectedAppId!),
    enabled: !!selectedAppId,
  });

  // Fetch decision engine configs for selected app
  const { data: decisionEngineConfigs } = useQuery({
    queryKey: ["decisionEngineConfigs", selectedAppId],
    queryFn: () => apiClient.getDecisionEngineConfigIds(selectedAppId!),
    enabled: !!selectedAppId,
  });

  // Auto-select configs if only one option (must be in useEffect to avoid setState during render)
  useEffect(() => {
    if (llmConfigs?.length === 1 && !selectedLlmConfigId) {
      setSelectedLlmConfigId(llmConfigs[0]);
    }
  }, [llmConfigs, selectedLlmConfigId, setSelectedLlmConfigId]);

  useEffect(() => {
    if (decisionEngineConfigs?.length === 1 && !selectedDecisionEngineConfigId) {
      setSelectedDecisionEngineConfigId(decisionEngineConfigs[0]);
    }
  }, [decisionEngineConfigs, selectedDecisionEngineConfigId, setSelectedDecisionEngineConfigId]);

  if (loadingApps) {
    return (
      <div className={`${isCollapsed ? 'w-16' : 'w-80'} bg-white border-r border-gray-200 p-6 transition-all duration-300`}>
        <div className="flex items-center justify-center h-32">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  if (appsError) {
    return (
      <div className={`${isCollapsed ? 'w-16' : 'w-80'} bg-white border-r border-gray-200 p-6 transition-all duration-300`}>
        <div className="flex flex-col items-center justify-center h-32 text-red-600">
          <AlertCircle className="h-8 w-8 mb-2" />
          {!isCollapsed && <p className="text-sm text-center">Failed to load applications</p>}
        </div>
      </div>
    );
  }

  return (
    <div className={`${isCollapsed ? 'w-16' : 'w-80'} bg-white border-r border-gray-200 flex flex-col h-full overflow-hidden transition-all duration-300 relative`}>
      {/* Toggle Button */}
      <button
        onClick={toggleCollapse}
        className="absolute top-4 right-3 z-10 p-1.5 rounded-md hover:bg-gray-100 transition-colors"
        aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {isCollapsed ? (
          <ChevronRight className="h-5 w-5 text-gray-600" />
        ) : (
          <ChevronLeft className="h-5 w-5 text-gray-600" />
        )}
      </button>

      {isCollapsed ? (
        /* Collapsed View - Icon Only */
        <div className="flex flex-col items-center gap-6 py-6 overflow-y-auto">
          {/* App Icons */}
          {appIds?.map((appId) => (
            <button
              key={appId}
              onClick={() => handleAppSelect(appId)}
              className={`p-2 rounded-lg transition-all ${selectedAppId === appId
                  ? "bg-blue-600 text-white"
                  : "text-gray-600 hover:bg-gray-100"
                }`}
              title={appId}
            >
              <Server className="h-5 w-5" />
            </button>
          ))}

          {/* Locale Indicator */}
          {selectedLocale && (
            <div className="mt-4 p-2 bg-blue-50 rounded-lg">
              <Globe className="h-5 w-5 text-blue-600" />
            </div>
          )}
        </div>
      ) : (
        /* Expanded View - Full Content */
        <>
          {/* Application Selection */}
          <div className="p-6 pt-14 border-b border-gray-200 overflow-y-auto">
            <div className="flex items-center gap-2 mb-4">
              <Server className="h-5 w-5 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">Application</h2>
            </div>

            <div className="space-y-2">
              {appIds?.map((appId) => (
                <button
                  key={appId}
                  onClick={() => handleAppSelect(appId)}
                  className={`w-full text-left px-4 py-3 rounded-lg border-2 transition-all ${selectedAppId === appId
                      ? "border-blue-600 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className={`font-medium capitalize ${selectedAppId === appId ? "text-blue-900" : "text-gray-900"
                        }`}>
                        {appId}
                      </p>
                    </div>
                    {selectedAppId === appId ? (
                      <CheckCircle2 className="h-5 w-5 text-blue-600" />
                    ) : (
                      <Circle className="h-5 w-5 text-gray-400" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Locale Selection */}
          {selectedAppId && (
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center gap-2 mb-4">
                <Globe className="h-5 w-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Language</h2>
              </div>

              {loadingLocales ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {locales?.map((locale) => (
                    <Button
                      key={locale}
                      variant={selectedLocale === locale ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedLocale(locale)}
                      className="uppercase"
                    >
                      {locale}
                    </Button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* LLM Config Selection */}
          {selectedAppId && llmConfigs && llmConfigs.length > 1 && (
            <div className="p-6 border-b border-gray-200">
              <div className="mb-3">
                <h3 className="text-sm font-semibold text-gray-900 mb-1">LLM Configuration</h3>
                <p className="text-xs text-gray-500">Language model settings</p>
              </div>

              <div className="space-y-1">
                {llmConfigs.map((config) => (
                  <button
                    key={config}
                    onClick={() => setSelectedLlmConfigId(config)}
                    className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${selectedLlmConfigId === config
                        ? "bg-blue-100 text-blue-900 font-medium"
                        : "hover:bg-gray-100 text-gray-700"
                      }`}
                  >
                    {config}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Decision Engine Config Selection */}
          {selectedAppId && decisionEngineConfigs && decisionEngineConfigs.length > 1 && (
            <div className="p-6">
              <div className="mb-3">
                <h3 className="text-sm font-semibold text-gray-900 mb-1">Decision Engine</h3>
                <p className="text-xs text-gray-500">Rule engine configuration</p>
              </div>

              <div className="space-y-1">
                {decisionEngineConfigs.map((config) => (
                  <button
                    key={config}
                    onClick={() => setSelectedDecisionEngineConfigId(config)}
                    className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${selectedDecisionEngineConfigId === config
                        ? "bg-blue-100 text-blue-900 font-medium"
                        : "hover:bg-gray-100 text-gray-700"
                      }`}
                  >
                    {config}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Configuration Summary */}
          {selectedAppId && selectedLocale && (
            <div className="mt-auto p-6 bg-gray-50 border-t border-gray-200">
              <h3 className="text-xs font-semibold text-gray-600 uppercase mb-3">
                Current Configuration
              </h3>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-gray-500">Application</p>
                  <p className="text-sm font-medium text-gray-900 capitalize">{selectedAppId}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Locale</p>
                  <Badge variant="secondary" className="uppercase">{selectedLocale}</Badge>
                </div>
                {selectedLlmConfigId && (
                  <div>
                    <p className="text-xs text-gray-500">LLM Config</p>
                    <p className="text-sm font-medium text-gray-900">{selectedLlmConfigId}</p>
                  </div>
                )}
                {selectedDecisionEngineConfigId && (
                  <div>
                    <p className="text-xs text-gray-500">Decision Engine</p>
                    <p className="text-sm font-medium text-gray-900">{selectedDecisionEngineConfigId}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

