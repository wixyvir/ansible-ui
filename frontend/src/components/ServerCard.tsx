import { Server } from 'lucide-react';
import { type Host } from '../types/ansible';
import { PlayCard } from './PlayCard';

interface ServerCardProps {
  host: Host;
}

export function ServerCard({ host }: ServerCardProps) {
  const getOverallStatusColor = () => {
    const hasFailedPlays = host.plays.some(play => play.status === 'failed');
    const hasChangedPlays = host.plays.some(play => play.status === 'changed');

    if (hasFailedPlays) return 'text-red-400';
    if (hasChangedPlays) return 'text-yellow-400';
    return 'text-green-400';
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 shadow-lg">
      <div className="flex items-center gap-2 mb-3">
        <Server className={`w-6 h-6 ${getOverallStatusColor()}`} />
        <h3 className="text-base font-semibold text-slate-100">{host.hostname}</h3>
      </div>

      <div className="space-y-2">
        {host.plays.map((play) => (
          <PlayCard key={play.id} play={play} />
        ))}
      </div>
    </div>
  );
}
