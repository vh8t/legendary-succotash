# Dokumentace: File Vault Projekt

Tento projekt je bezpečné webové úložiště souborů (Vault), které umožňuje uživatelům nahrávat, spravovat a stahovat soubory prostřednictvím moderního webového rozhraní.

## O projektu
Cílem projektu bylo vytvořit funkční a bezpečný systém pro ukládání dat s důrazem na jednoduchost nasazení pomocí kontejnerizace a automatizaci běžných úkolů (vytváření uživatelů, archivace).

## Architektura systému

Projekt je rozdělen do tří hlavních částí:

### 1. Backend (FastAPI)
Srdcem aplikace je Python server postavený na frameworku **FastAPI**.
- **Databáze:** Používá `aiosqlite` (SQLite) pro ukládání informací o uživatelích a metadat o souborech.
- **Zabezpečení:** Autentizace probíhá pomocí **JWT (JSON Web Tokens)**. Hesla jsou v databázi hashována pomocí algoritmu `bcrypt`.
- **API Endpointy:** Zahrnují přihlašování, výpis souborů, nahrávání, stahování a mazání souborů.

### 2. Frontend (SvelteKit)
Uživatelské rozhraní je postaveno na moderním frameworku **Svelte 5**.
- **Styling:** Využívá **Tailwind CSS** pro responzivní a čistý design.
- **Komponenty:** Používá knihovny `bits-ui` a `lucide-svelte` pro interaktivní prvky a ikony.
- **Správa stavu:** Využívá Svelte Runes pro efektivní správu stavu přihlášení a seznamu souborů.

### 3. Infrastruktura a Skripty
Projekt je připraven pro snadné nasazení a údržbu.
- **Docker:** Backend i frontend mají vlastní `Containerfile` pro izolovaný běh. Frontend je v produkci servírován přes **Nginx**.
- **Automatizace:** Ve složce `scripts/` se nacházejí pomocné Bash skripty:
  - `dev-server`: Spustí vývojové prostředí.
  - `deploy`: Sestaví a spustí kontejnery.
  - `create-user`: Přidá nového uživatele do systému.
  - `archive-files`: Zabalí soubory starší než 30 dní do `.tar.gz` archivu pro úsporu místa.

## Jak to funguje

1. **Přihlášení:** Uživatel se přihlásí pomocí jména a hesla. Server ověří údaje a vrátí JWT token.
2. **Nahrávání:** Po autorizaci může uživatel nahrát soubory. Server uloží soubor na disk do složky `data/vault_data` a zapíše záznam do databáze.
3. **Správa:** Uživatelé vidí seznam všech nahraných souborů, ale mazat mohou pouze ty, které sami nahráli.
4. **Archivace:** Systém umožňuje automatické čištění úložiště přesouváním starých dat do komprimovaných archivů.

## Požadavky pro spuštění
- Python 3.11+
- Node.js & npm (pro frontend)
- Docker (pro produkční nasazení)

## Instalace a spuštění
Pro rychlé spuštění vývojového prostředí lze použít skript v kořenovém adresáři:
```bash
./scripts/dev-server
```
Pro nasazení v kontejnerech:
```bash
./scripts/deploy
```
