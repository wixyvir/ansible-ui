import { useState } from 'react';
import { Loader2, Copy, Check } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { type PlayStatus, type Task } from '../types/ansible';
import { StatusBadge } from './StatusBadge';
import { fetchTasks } from '../services/api';

interface CollapsibleTaskSectionProps {
  playId: string;
  status: PlayStatus;
  count: number;
  label: string;
}

export function CollapsibleTaskSection({
  playId,
  status,
  count,
  label,
}: CollapsibleTaskSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [tasks, setTasks] = useState<Task[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedTaskId, setCopiedTaskId] = useState<string | null>(null);

  const handleCopy = async (taskId: string, text: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedTaskId(taskId);
    setTimeout(() => setCopiedTaskId(null), 2000);
  };

  const handleToggle = async () => {
    if (count === 0) return;

    const newExpanded = !isExpanded;
    setIsExpanded(newExpanded);

    // Fetch tasks on first expand only
    if (newExpanded && tasks === null) {
      setLoading(true);
      setError(null);
      try {
        const fetchedTasks = await fetchTasks(playId, status);
        setTasks(fetchedTasks);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load tasks';
        setError(message);
      } finally {
        setLoading(false);
      }
    }
  };

  const isDisabled = count === 0;

  return (
    <div>
      <StatusBadge
        status={status}
        count={count}
        label={label}
        disabled={isDisabled}
        expanded={isExpanded}
        showChevron={!isDisabled}
        onClick={handleToggle}
      />

      {isExpanded && (
        <div className="ml-2 mt-2 space-y-2 text-sm text-slate-300">
          {loading && (
            <div className="flex items-center gap-2 text-slate-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading tasks...</span>
            </div>
          )}

          {error && (
            <div className="text-red-400 text-xs">
              {error}
            </div>
          )}

          {tasks && tasks.length > 0 && (
            <ul className="space-y-2">
              {tasks.map((task) => (
                <li key={task.id}>
                  <div className="flex items-start gap-2">
                    <span className="text-slate-500 select-none">•</span>
                    <div className="flex-1 min-w-0">
                      <span>{task.name}</span>
                      {task.failure_message && (
                        <div className="mt-1.5 rounded border border-slate-600 overflow-hidden max-h-48 overflow-y-auto relative group">
                          <button
                            onClick={() => handleCopy(task.id, task.failure_message!)}
                            className="absolute top-1 right-1 p-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-400 hover:text-slate-200 opacity-0 group-hover:opacity-100 transition-opacity z-10"
                            title="Copy to clipboard"
                          >
                            {copiedTaskId === task.id ? (
                              <Check className="w-3.5 h-3.5 text-green-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                          <SyntaxHighlighter
                            language="json"
                            style={oneDark}
                            customStyle={{
                              margin: 0,
                              padding: '0.5rem',
                              fontSize: '0.75rem',
                              background: '#1e293b',
                              whiteSpace: 'pre-wrap',
                              wordBreak: 'break-word',
                            }}
                            wrapLongLines
                          >
                            {task.failure_message}
                          </SyntaxHighlighter>
                        </div>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {tasks && tasks.length === 0 && !loading && (
            <div className="text-slate-400 text-xs">
              No tasks found
            </div>
          )}
        </div>
      )}
    </div>
  );
}
