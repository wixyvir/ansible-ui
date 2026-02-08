interface AnsibleauConfig {
  backendUri: string;
}

declare global {
  interface Window {
    ANSIBEAU_CONFIG: AnsibleauConfig;
  }
}

export {};
