import { useState } from 'react';
import { Loader2 } from 'lucide-react';
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
                    <div className="flex-1">
                      <span>{task.name}</span>
                      {task.failure_message && (
                        <div className="text-xs text-slate-400 mt-0.5 ml-2">
                          {task.failure_message}
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
