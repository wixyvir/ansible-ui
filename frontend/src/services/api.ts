import { Log, Task, PlayStatus } from '../types/ansible';

const getBackendUri = (): string => {
  const config = window.ANSIBEAU_CONFIG;
  if (config && typeof config.backendUri === 'string') {
    return config.backendUri.replace(/\/+$/, '');
  }
  return 'http://localhost:8000';
};

export const fetchLog = async (logId: string): Promise<Log> => {
  const backendUri = getBackendUri();
  let response: Response;

  try {
    response = await fetch(`${backendUri}/api/logs/${logId}/`);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    throw new Error(`Failed to connect to backend at ${backendUri}: ${message}`);
  }

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Log not found');
    }
    throw new Error(`Failed to fetch log: ${response.status} ${response.statusText}`);
  }
  return response.json();
};

export const fetchTasks = async (playId: string, status: PlayStatus): Promise<Task[]> => {
  const backendUri = getBackendUri();
  let response: Response;

  try {
    response = await fetch(`${backendUri}/api/plays/${playId}/tasks/?status=${status}`);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    throw new Error(`Failed to connect to backend at ${backendUri}: ${message}`);
  }

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Play not found');
    }
    throw new Error(`Failed to fetch tasks: ${response.status} ${response.statusText}`);
  }
  return response.json();
};
