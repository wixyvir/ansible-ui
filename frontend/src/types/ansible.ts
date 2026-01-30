export type PlayStatus = 'ok' | 'changed' | 'failed';

export type TaskStatus = 'ok' | 'changed' | 'failed' | 'fatal' | 'skipping' | 'unreachable' | 'ignored' | 'rescued';

export interface Task {
  id: string;
  name: string;
  order: number;
  line_number: number | null;
  status: TaskStatus;
  failure_message: string | null;
}

export interface TaskSummary {
  ok: number;
  changed: number;
  failed: number;
}

export interface Play {
  id: string;
  name: string;
  date: string | null;
  status: PlayStatus;
  tasks: TaskSummary;
}

export interface Host {
  id: string;
  hostname: string;
  plays: Play[];
}

export interface Log {
  id: string;
  title: string;
  uploaded_at: string;
  hosts: Host[];
  host_count: number;
}
