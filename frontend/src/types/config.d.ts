interface AnsibleUIConfig {
  backendUri: string;
}

declare global {
  interface Window {
    ANSIBLE_UI_CONFIG: AnsibleUIConfig;
  }
}

export {};
