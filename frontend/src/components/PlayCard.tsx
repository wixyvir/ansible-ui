import { useState } from 'react';
import { Calendar, ChevronDown, ChevronUp } from 'lucide-react';
import { type Play } from '../types/ansible';
import { CollapsibleTaskSection } from './CollapsibleTaskSection';

interface PlayCardProps {
  play: Play;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function PlayCard({ play }: PlayCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusColor = () => {
    if (play.tasks.failed > 0) return 'text-red-400';
    if (play.tasks.changed > 0) return 'text-yellow-400';
    return 'text-green-400';
  };

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="bg-slate-700 border border-slate-600 rounded-md p-3">
      <div className="flex items-center justify-between mb-2">
        <h4
          className={`text-sm font-semibold ${getStatusColor()} cursor-pointer hover:opacity-80 transition-opacity`}
          onClick={handleToggle}
        >
          {play.name}
        </h4>
        <div className="flex items-center gap-2">
          {play.date && (
            <div className="flex items-center gap-1 text-slate-400 text-xs">
              <Calendar className="w-3.5 h-3.5" />
              <span>{formatDate(play.date)}</span>
            </div>
          )}
          <button
            onClick={handleToggle}
            className="text-slate-400 hover:text-slate-200 transition-colors"
            aria-label={isExpanded ? 'Collapse task details' : 'Expand task details'}
          >
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="space-y-1.5">
          <CollapsibleTaskSection playId={play.id} status="ok" count={play.tasks.ok} label="OK" />
          <CollapsibleTaskSection playId={play.id} status="changed" count={play.tasks.changed} label="Changed" />
          <CollapsibleTaskSection playId={play.id} status="failed" count={play.tasks.failed} label="Failed" />
        </div>
      )}
    </div>
  );
}
