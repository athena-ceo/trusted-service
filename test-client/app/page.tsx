"use client";

import { useEffect } from "react";
import Image from "next/image";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useTestClientStore } from "@/lib/store/useTestClientStore";
import { Sidebar } from "@/components/test-client/sidebar";

export default function Home() {
  const {
    selectedAppId,
    selectedLocale,
  } = useTestClientStore();

  // Fetch app metadata when app and locale are selected
  const { data: appNameData } = useQuery({
    queryKey: ["appName", selectedAppId, selectedLocale],
    queryFn: () => apiClient.getAppName(selectedAppId!, selectedLocale!),
    enabled: !!selectedAppId && !!selectedLocale,
  });

  const { data: appDescription } = useQuery({
    queryKey: ["appDescription", selectedAppId, selectedLocale],
    queryFn: () => apiClient.getAppDescription(selectedAppId!, selectedLocale!),
    enabled: !!selectedAppId && !!selectedLocale,
  });

  const { data: sampleMessage } = useQuery({
    queryKey: ["sampleMessage", selectedAppId, selectedLocale],
    queryFn: () => apiClient.getSampleMessage(selectedAppId!, selectedLocale!),
    enabled: !!selectedAppId && !!selectedLocale,
  });

  // Update document title when app is selected
  useEffect(() => {
    if (appNameData) {
      document.title = `${appNameData} | Trusted Services Test Client`;
    } else if (selectedAppId) {
      document.title = `${selectedAppId} | Trusted Services Test Client`;
    } else {
      document.title = "Trusted Services Test Client";
    }
  }, [appNameData, selectedAppId]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Image
                src="/athena-logo.svg"
                alt="Athena Decision Systems"
                width={200}
                height={60}
                className="h-12 w-auto"
                priority
              />
              <div className="border-l-2 border-gray-300 pl-4">
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl font-bold text-gray-900">
                    Trusted Services Test Client
                  </h1>
                  {selectedAppId && (
                    <>
                      <span className="text-gray-300">•</span>
                      <span className="text-xl font-semibold text-blue-600 capitalize">
                        {appNameData || selectedAppId}
                      </span>
                      {selectedLocale && (
                        <Badge variant="secondary" className="uppercase text-xs">
                          {selectedLocale}
                        </Badge>
                      )}
                    </>
                  )}
                </div>
                <p className="text-sm text-gray-500">
                  Modern testing interface for all applications
                </p>
              </div>
            </div>
            <Badge variant="success">v2.0</Badge>
          </div>
        </div>
      </header>

      {/* Main Layout with Sidebar */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-6xl mx-auto px-8 py-8">
            {!selectedAppId ? (
              <Card className="border-2 border-dashed border-gray-300">
                <CardContent className="py-12 text-center">
                  <div className="max-w-md mx-auto">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-3xl">👈</span>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Select an Application
                    </h3>
                    <p className="text-gray-600">
                      Choose an application from the sidebar to get started
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : !selectedLocale ? (
              <Card className="border-2 border-dashed border-gray-300">
                <CardContent className="py-12 text-center">
                  <div className="max-w-md mx-auto">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-3xl">🌍</span>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Select a Language
                    </h3>
                    <p className="text-gray-600">
                      Choose a locale from the sidebar to continue
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-6">
                {/* Application Info Card */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-2xl">
                          {appNameData || selectedAppId}
                        </CardTitle>
                        <CardDescription className="mt-2">
                          {appDescription || "Loading description..."}
                        </CardDescription>
                      </div>
                      <Badge variant="success" className="text-sm">
                        {selectedLocale?.toUpperCase()}
                      </Badge>
                    </div>
                  </CardHeader>
                  {sampleMessage && (
                    <CardContent>
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <p className="text-sm font-medium text-blue-900 mb-2">
                          Sample Message:
                        </p>
                        <p className="text-sm text-blue-800 italic">
                          "{sampleMessage}"
                        </p>
                      </div>
                    </CardContent>
                  )}
                </Card>

                {/* Workflow Status */}
                <Card>
                  <CardHeader>
                    <CardTitle>Test Workflow</CardTitle>
                    <CardDescription>
                      Ready to test the complete workflow
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                          <span className="text-green-600 font-semibold text-sm">✓</span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Application Selected</p>
                          <p className="text-sm text-gray-600 capitalize">{selectedAppId}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                          <span className="text-green-600 font-semibold text-sm">✓</span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Locale Configured</p>
                          <p className="text-sm text-gray-600 uppercase">{selectedLocale}</p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                          <span className="text-blue-600 font-semibold text-sm">→</span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Next: Build Workflow UI</p>
                          <p className="text-sm text-gray-600">
                            Stage 1: Input form • Stage 2: Analysis • Stage 3: Results
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>
              © {new Date().getFullYear()} Athena Decision Systems. All rights reserved.
            </p>
            <p className="text-gray-500">
              Trusted Services Framework v2.0
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
