import { Log } from '../types/ansible';

const getBackendUri = (): string => {
  return window.ANSIBLE_UI_CONFIG?.backendUri || 'http://localhost:8000';
};

export const fetchLog = async (logId: string): Promise<Log> => {
  const response = await fetch(`${getBackendUri()}/api/logs/${logId}/`);
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Log not found');
    }
    throw new Error(`Failed to fetch log: ${response.status}`);
  }
  return response.json();
};
