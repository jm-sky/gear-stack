// Registry i18n messages - Polish
// This file contains common messages shared across all registry components
// Module-specific messages (auth, logs, settings, user) are in their respective modules
// To use module translations, import and merge them in your project's i18n config
// Example: import { authPl } from '@/modules/auth/i18n'

export default {
  common: {
    welcome: 'Witaj',
    loading: 'Ładowanie...',
    error: 'Błąd',
    success: 'Sukces',
    cancel: 'Anuluj',
    save: 'Zapisz',
    delete: 'Usuń',
    edit: 'Edytuj',
    close: 'Zamknij',
    confirm: 'Potwierdź',
    search: 'Szukaj',
    filter: 'Filtruj',
    sort: 'Sortuj',
    actions: 'Akcje',
    yes: 'Tak',
    no: 'Nie',
    previous: 'Poprzedni',
    next: 'Następny',
    columns: 'Kolumny',
    open_menu: 'Otwórz menu',
    back: 'Wstecz',
    done: 'Gotowe',
    never: 'Nigdy',
    copyToClipboard: {
      success: 'Skopiowano do schowka',
      copied: 'Skopiowano',
      copy: 'Skopiuj',
    },
    pagination: {
      totalRows: 'Łącznie {total} wierszy',
      rowsPerPage: 'Wierszy na stronę',
      page: 'Strona',
      of: 'z',
      goToFirstPage: 'Przejdź do pierwszej strony',
      goToPreviousPage: 'Przejdź do poprzedniej strony',
      goToNextPage: 'Przejdź do następnej strony',
      goToLastPage: 'Przejdź do ostatniej strony',
    },
  },
  validation: {
    required: 'To pole jest wymagane',
    email: 'Nieprawidłowy adres email',
    min: 'Musi mieć co najmniej {min} znaków',
    min_length: 'Musi mieć co najmniej {min} znaków',
    max: 'Może mieć maksymalnie {max} znaków',
    password_mismatch: 'Hasła nie są identyczne',
    password_too_short: 'Hasło musi mieć co najmniej {min} znaków',
    invalid_token: 'Nieprawidłowy lub wygasły token',
  },
  errors: {
    generic: 'Wystąpił błąd. Spróbuj ponownie',
    network: 'Błąd sieci. Sprawdź połączenie internetowe',
    unauthorized: 'Nie masz uprawnień do wykonania tej akcji',
    not_found: 'Zasób nie został znaleziony',
    server_error: 'Błąd serwera. Spróbuj ponownie później',
  },
  navigation: {
    dashboard: 'Panel',
    profile: 'Profil',
    settings: 'Ustawienia',
  },
  auth: {
    logout: 'Wyloguj',
  },
  user: {
    profile: {
      title: 'Profil',
    },
  },
  settings: {
    page: {
      title: 'Ustawienia',
    },
  },
  footer: {
    cookies: 'Informacja o ciasteczkach',
    privacy: 'Polityka prywatności',
    contact: 'Kontakt',
    github: 'GitHub',
  },
  cookies: {
    title: 'Informacja o ciasteczkach',
    subtitle: 'Informacje o wykorzystaniu danych w aplikacji',
    localStorage: {
      title: 'LocalStorage',
      description: 'Aplikacja Gear Stack wykorzystuje localStorage przeglądarki do przechowywania danych użytkownika. Wszystkie dane są przechowywane lokalnie na Twoim urządzeniu i nie są przesyłane na żadne zewnętrzne serwery.',
    },
    whatWeStore: {
      title: 'Co przechowujemy',
      items: 'Dane kontenerów i przedmiotów (nazwy, opisy, wagi, statusy)',
      profile: 'Dane profilu użytkownika (nazwa, email)',
      settings: 'Ustawienia aplikacji (język, preferencje)',
    },
    privacy: {
      title: 'Prywatność',
      description: 'Wszystkie dane są przechowywane wyłącznie w Twojej przeglądarce. Nie zbieramy, nie przetwarzamy ani nie udostępniamy Twoich danych osobom trzecim. Aplikacja działa w pełni po stronie klienta (client-side).',
    },
    future: {
      title: 'Przyszłość',
      description: 'W przyszłości aplikacja może wykorzystywać cookies do dodatkowych funkcji (np. synchronizacja między urządzeniami). W takim przypadku ta strona zostanie zaktualizowana o szczegółowe informacje.',
    },
    rodo: {
      title: 'RODO',
      description: 'Zgodnie z Rozporządzeniem Ogólnym o Ochronie Danych (RODO), informujemy, że aplikacja nie przetwarza danych osobowych w sposób wymagający zgody użytkownika, ponieważ wszystkie dane są przechowywane lokalnie na urządzeniu użytkownika.',
    },
  },
  privacy: {
    title: 'Polityka prywatności',
    subtitle: 'Jak chronimy Twoje dane',
    dataStorage: {
      title: 'Przechowywanie danych',
      description: 'Aplikacja Gear Stack przechowuje wszystkie dane lokalnie w przeglądarce użytkownika za pomocą localStorage. Dane nie są przesyłane na żadne zewnętrzne serwery ani do osób trzecich.',
    },
    dataAccess: {
      title: 'Dostęp do danych',
      description: 'Tylko Ty masz dostęp do swoich danych. Aplikacja nie wymaga rejestracji ani logowania, więc nie ma możliwości, aby ktokolwiek inny uzyskał dostęp do Twoich danych.',
    },
    dataDeletion: {
      title: 'Usuwanie danych',
      description: 'Możesz w każdej chwili usunąć wszystkie dane z aplikacji poprzez wyczyszczenie localStorage w ustawieniach przeglądarki lub użycie funkcji eksportu/usuwania danych w aplikacji.',
    },
    changes: {
      title: 'Zmiany w polityce',
      description: 'W przypadku wprowadzenia zmian w sposobie przetwarzania danych, ta strona zostanie zaktualizowana, a użytkownicy zostaną poinformowani o istotnych zmianach.',
    },
  },
  contact: {
    title: 'Kontakt',
    subtitle: 'Skontaktuj się z nami',
    info: {
      title: 'Informacje kontaktowe',
      description: 'Jeśli masz pytania, sugestie lub chcesz zgłosić problem, skontaktuj się z nami:',
    },
    email: {
      label: 'Email',
    },
    support: {
      title: 'Wsparcie',
      description: 'Staramy się odpowiadać na wszystkie wiadomości w ciągu 7 dni. Jeśli zgłaszasz problem techniczny, prosimy o dołączenie szczegółowych informacji o problemie.',
    },
  },
}
