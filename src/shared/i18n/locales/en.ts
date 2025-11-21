// Registry i18n messages - English
// This file contains common messages shared across all registry components
// Module-specific messages (auth, logs, settings, user) are in their respective modules
// To use module translations, import and merge them in your project's i18n config
// Example: import { authEn } from '@/modules/auth/i18n'

export default {
  common: {
    welcome: 'Welcome',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    close: 'Close',
    confirm: 'Confirm',
    search: 'Search',
    filter: 'Filter',
    sort: 'Sort',
    actions: 'Actions',
    yes: 'Yes',
    no: 'No',
    previous: 'Previous',
    next: 'Next',
    columns: 'Columns',
    open_menu: 'Open menu',
    back: 'Back',
    done: 'Done',
    never: 'Never',
    or: 'or',
    copyToClipboard: {
      success: 'Copied to clipboard',
      copied: 'Copied',
      copy: 'Copy',
    },
    pagination: {
      totalRows: '{total} row(s) total',
      rowsPerPage: 'Rows per page',
      page: 'Page',
      of: 'of',
      goToFirstPage: 'Go to first page',
      goToPreviousPage: 'Go to previous page',
      goToNextPage: 'Go to next page',
      goToLastPage: 'Go to last page',
    },
  },
  validation: {
    required: 'This field is required',
    email: 'Invalid email address',
    min: 'Must be at least {min} characters',
    min_length: 'Must be at least {min} characters',
    max: 'Must be at most {max} characters',
    password_mismatch: 'Passwords do not match',
    password_too_short: 'Password must be at least {min} characters',
    invalid_token: 'Invalid or expired token',
  },
  errors: {
    generic: 'An error occurred. Please try again',
    network: 'Network error. Please check your connection',
    unauthorized: 'You are not authorized to perform this action',
    not_found: 'Resource not found',
    server_error: 'Server error. Please try again later',
  },
  navigation: {
    dashboard: 'Dashboard',
    profile: 'Profile',
    settings: 'Settings',
  },
  auth: {
    logout: 'Logout',
  },
  user: {
    profile: {
      title: 'Profile',
    },
  },
  settings: {
    page: {
      title: 'Settings',
    },
  },
  footer: {
    cookies: 'Cookie Information',
    privacy: 'Privacy Policy',
    contact: 'Contact',
    github: 'GitHub',
  },
  cookies: {
    title: 'Cookie Information',
    subtitle: 'Information about data usage in the application',
    localStorage: {
      title: 'LocalStorage',
      description: 'Gear Stack application uses browser localStorage to store user data. All data is stored locally on your device and is not sent to any external servers.',
    },
    whatWeStore: {
      title: 'What we store',
      items: 'Container and item data (names, descriptions, weights, statuses)',
      profile: 'User profile data (name, email)',
      settings: 'Application settings (language, preferences)',
    },
    privacy: {
      title: 'Privacy',
      description: 'All data is stored exclusively in your browser. We do not collect, process, or share your data with third parties. The application runs fully client-side.',
    },
    future: {
      title: 'Future',
      description: 'In the future, the application may use cookies for additional features (e.g., synchronization between devices). In such case, this page will be updated with detailed information.',
    },
    rodo: {
      title: 'GDPR',
      description: 'In accordance with the General Data Protection Regulation (GDPR), we inform that the application does not process personal data in a way that requires user consent, as all data is stored locally on the user\'s device.',
    },
  },
  privacy: {
    title: 'Privacy Policy',
    subtitle: 'How we protect your data',
    dataStorage: {
      title: 'Data Storage',
      description: 'Gear Stack application stores all data locally in the user\'s browser using localStorage. Data is not sent to any external servers or third parties.',
    },
    dataAccess: {
      title: 'Data Access',
      description: 'Only you have access to your data. The application does not require registration or login, so there is no way for anyone else to access your data.',
    },
    dataDeletion: {
      title: 'Data Deletion',
      description: 'You can delete all data from the application at any time by clearing localStorage in your browser settings or using the export/delete data function in the application.',
    },
    changes: {
      title: 'Policy Changes',
      description: 'In case of changes in the way data is processed, this page will be updated, and users will be informed about significant changes.',
    },
  },
  contact: {
    title: 'Contact',
    subtitle: 'Get in touch with us',
    info: {
      title: 'Contact Information',
      description: 'If you have questions, suggestions, or want to report a problem, please contact us:',
    },
    email: {
      label: 'Email',
    },
    support: {
      title: 'Support',
      description: 'We try to respond to all messages within 7 days. If you are reporting a technical issue, please include detailed information about the problem.',
    },
  },
}
