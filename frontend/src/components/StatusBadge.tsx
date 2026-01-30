import { ChevronDown, ChevronUp } from 'lucide-react';
import { type PlayStatus } from '../types/ansible';

interface StatusBadgeProps {
  status: PlayStatus;
  count: number;
  label: string;
  disabled?: boolean;
  expanded?: boolean;
  showChevron?: boolean;
  onClick?: () => void;
}

const statusStyles: Record<PlayStatus, string> = {
  ok: 'bg-green-900/50 text-green-400 border-green-700',
  changed: 'bg-yellow-900/50 text-yellow-400 border-yellow-700',
  failed: 'bg-red-900/50 text-red-400 border-red-700',
};

export function StatusBadge({
  status,
  count,
  label,
  disabled = false,
  expanded = false,
  showChevron = false,
  onClick,
}: StatusBadgeProps) {
  const isClickable = !disabled && onClick;

  return (
    <div
      className={`flex items-center justify-between px-3 py-2 rounded-lg border ${statusStyles[status]} ${
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      } ${isClickable ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}`}
      onClick={isClickable ? onClick : undefined}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onKeyDown={
        isClickable
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick?.();
              }
            }
          : undefined
      }
    >
      <span className="text-sm font-medium">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-lg font-bold">{count}</span>
        {showChevron && !disabled && (
          expanded ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )
        )}
      </div>
    </div>
  );
}
