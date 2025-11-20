# Konfiguracja uprawnień dla deploymentu

## Krok 1: Dodaj użytkownika "deploy" do grupy "caddy"

```bash
sudo usermod -a -G caddy deploy
```

## Krok 2: Ustaw uprawnienia na katalogu /var/www/gear-stack

```bash
# Ustaw właściciela i grupę
sudo chown -R caddy:caddy /var/www/gear-stack

# Ustaw uprawnienia: właściciel i grupa mogą zapisywać, inni tylko czytać
sudo chmod -R 775 /var/www/gear-stack

# Ustaw setgid bit, aby nowe pliki dziedziczyły grupę
sudo chmod g+s /var/www/gear-stack
```

## Krok 3: Wyloguj i zaloguj się ponownie jako użytkownik "deploy"

Uprawnienia grupowe wymagają wylogowania:

```bash
# Sprawdź czy użytkownik jest w grupie caddy
groups deploy

# Jeśli nie widzisz "caddy", wyloguj się i zaloguj ponownie
```

## Alternatywa: Konfiguracja sudoers (jeśli powyższe nie działa)

Jeśli chcesz używać sudo w skrypcie, skonfiguruj sudoers:

```bash
sudo visudo
```

Dodaj linię:
```
deploy ALL=(ALL) NOPASSWD: /usr/bin/rsync, /usr/bin/mkdir
```

## Weryfikacja

Przetestuj uprawnienia:

```bash
# Jako użytkownik deploy
touch /var/www/gear-stack/test.txt
rm /var/www/gear-stack/test.txt
```

Jeśli działa bez sudo, konfiguracja jest poprawna.

