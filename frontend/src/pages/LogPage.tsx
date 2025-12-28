import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ServerCard } from '../components/ServerCard';
import { fetchLog } from '../services/api';
import { type Host, type Log } from '../types/ansible';

function LogPage() {
  const { logId } = useParams<{ logId: string }>();
  const [log, setLog] = useState<Log | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!logId) {
      setError('No log ID provided');
      setLoading(false);
      return;
    }

    const loadLog = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchLog(logId);
        setLog(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load log');
      } finally {
        setLoading(false);
      }
    };

    loadLog();
  }, [logId]);

  useEffect(() => {
    if (log) {
      document.title = `${log.title} - Ansible UI`;
    } else {
      document.title = 'Ansible UI - Play Results';
    }
  }, [log]);

  const getHostStatus = (host: Host) => {
    const hasFailedPlays = host.plays.some(play => play.status === 'failed');
    const hasChangedPlays = host.plays.some(play => play.status === 'changed');

    if (hasFailedPlays) return 'failed';
    if (hasChangedPlays) return 'changed';
    return 'ok';
  };

  const statusOrder = { failed: 0, changed: 1, ok: 2 };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 py-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-slate-400 text-lg">Loading...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 py-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col items-center justify-center h-64">
            <div className="text-red-400 text-lg mb-2">Error</div>
            <div className="text-slate-400">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (!log) {
    return (
      <div className="min-h-screen bg-slate-900 py-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-slate-400 text-lg">Log not found</div>
          </div>
        </div>
      </div>
    );
  }

  const sortedHosts = [...log.hosts].sort(
    (a, b) => statusOrder[getHostStatus(a)] - statusOrder[getHostStatus(b)]
  );

  return (
    <div className="min-h-screen bg-slate-900 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-5">
          <h1 className="text-3xl font-bold text-slate-100 mb-1">{log.title}</h1>
          <p className="text-slate-400 text-base">
            {new Date(log.uploaded_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        </div>

        {sortedHosts.length === 0 ? (
          <div className="text-slate-400 text-center py-8">
            No hosts found in this log
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sortedHosts.map((host) => (
              <ServerCard key={host.id} host={host} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default LogPage;
