'use client';

import { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';

interface PackageConditionEditorProps {
  runtime: string;
  app: string;
  packageName: string;
  currentCondition: string;
  onClose: () => void;
  onSave: (condition: string | null) => void;
}

export default function PackageConditionEditor({
  currentCondition,
  onClose,
  onSave,
}: PackageConditionEditorProps) {
  const [condition, setCondition] = useState(currentCondition);

  useEffect(() => {
    setCondition(currentCondition);
  }, [currentCondition]);

  const handleSave = () => {
    onSave(condition.trim() || null);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">Edit Package Condition</h3>
          <button
            onClick={onClose}
            className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Condition (optional)
            </label>
            <input
              type="text"
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              placeholder='e.g., input.field_values["departement"] == "78"'
              className="w-full px-3 py-2 border rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-2">
              Python expression that determines when this package executes.
              Leave empty to execute unconditionally.
            </p>
            <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
              <strong>Examples:</strong>
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li><code>input.field_values["departement"] == "78"</code></li>
                <li><code>input.intention_id == "expiration_d_une_api"</code></li>
                <li><code>input.field_values.get("status") == "active"</code></li>
              </ul>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 p-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Save className="w-4 h-4" />
            Save
          </button>
        </div>
      </div>
    </div>
  );
}



