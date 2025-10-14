# Technische Dokumentation der Datenbankstruktur

Dieses Dokument beschreibt das technische Schema der SQLite-Datenbank `pokemon_cards.db`

## Übersicht

Die Datenbank verwendet ein relationales Modell, um die Kartendaten normalisiert und effizient zu speichern. Sie besteht aus einer zentralen `cards`-Tabelle, mehreren Nachschlage-Tabellen (für wiederkehrende Werte wie Typen oder Seltenheiten) und Verbindungstabellen, um komplexe Beziehungen abzubilden.

---

### 1. Nachschlage-Tabellen (Lookup Tables)

Diese Tabellen speichern eindeutige, wiederverwendbare Werte.

| Tabelle | Spalte | Datentyp | Constraints | Beschreibung |
| :--- | :--- | :--- | :--- | :--- |
| **`set_eras`** | `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Eindeutige ID für eine Ära |
| | `name` | `TEXT` | `NOT NULL UNIQUE` | Name der Ära (z.B. "Schwert & Schild") |
| **`sets`** | `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Eindeutige ID für ein Set |
| | `name` | `TEXT` | `NOT NULL UNIQUE` | Name des Sets |
| | `era_id` | `INTEGER` | `FOREIGN KEY (set_eras.id)` | Verweis auf die Ära des Sets |
| | `release_date` | `TEXT` | | Veröffentlichungsdatum im Format YYYY-MM-DD |
| **`rarities`** | `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Eindeutige ID für eine Seltenheit |
| | `name` | `TEXT` | `NOT NULL UNIQUE` | Name der Seltenheit |
| **`types`** | `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Eindeutige ID für einen Typ |
| | `name` | `TEXT` | `NOT NULL UNIQUE` | Typenname (z.B. "Wasser", "Farblos") |
| **`subtypes`** | `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Eindeutige ID für einen Untertyp |
| | `name` | `TEXT` | `NOT NULL UNIQUE` | Untertyp-Name (z.B. "Phase-1", "Item") |

---

### 2. Zentrale Tabelle: `cards`

Das Herzstück der Datenbank, das die Kerninformationen jeder Karte enthält.

| Spalte | Datentyp | Constraints | Beschreibung |
| :--- | :--- | :--- | :--- |
| `id` | `TEXT` | `PRIMARY KEY` | Eindeutige Karten-ID (z.B. "sv05-135") |
| `name` | `TEXT` | `NOT NULL` | Name der Karte |
| `supertype` | `TEXT` | `NOT NULL` | Haupttyp ("Pokémon", "Trainer", "Energy") |
| `hp` | `INTEGER` | | Kraftpunkte (KP), `NULL` für Nicht-Pokémon |
| `evolvesFrom` | `TEXT` | | Name des Pokémon, aus dem es sich entwickelt |
| `artist` | `TEXT` | | Name des Illustrators |
| `image_path` | `TEXT` | `NOT NULL` | Relativer Pfad zum Bild der Karte |
| `number` | `TEXT` | | Kartennummer im Set (z.B. "135/162") |
| `set_id` | `INTEGER` | `FOREIGN KEY (sets.id)` | Verweis auf das Set der Karte |
| `rarity_id` | `INTEGER` | `FOREIGN KEY (rarities.id)` | Verweis auf die Seltenheit der Karte |

---

### 3. Eigenschafts-Tabellen (1-zu-N Beziehungen)

Diese Tabellen speichern Listen von Eigenschaften, die zu einer einzelnen Karte gehören.

| Tabelle | Spalte | Datentyp | Constraints | Beschreibung |
| :--- | :--- | :--- | :--- | :--- |
| **`attacks`** | `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Eindeutige ID für eine Attacke |
| | `card_id` | `TEXT` | `NOT NULL, FOREIGN KEY (cards.id)` | Karte, zu der die Attacke gehört |
| | `name` | `TEXT` | `NOT NULL` | Name der Attacke |
| | `damage` | `TEXT` | | Schaden (als Text, da "+", "x" etc. möglich) |
| | `text` | `TEXT` | | Beschreibungstext der Attacke |
| **`attack_costs`** | `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Eindeutige ID für einen Energiekosten-Eintrag |
| | `attack_id` | `INTEGER` | `NOT NULL, FOREIGN KEY (attacks.id)` | Attacke, zu der die Kosten gehören |
| | `cost_type` | `TEXT` | `NOT NULL` | Typ der benötigten Energie (z.B. "Wasser") |
| **`abilities`** | `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Eindeutige ID für eine Fähigkeit |
| | `card_id` | `TEXT` | `NOT NULL, FOREIGN KEY (cards.id)` | Karte, zu der die Fähigkeit gehört |
| | `name` | `TEXT` | `NOT NULL` | Name der Fähigkeit |
| | `text` | `TEXT` | | Beschreibungstext der Fähigkeit |
| | `type` | `TEXT` | `NOT NULL` | Art der Fähigkeit (z.B. "Ability", "Pokémon-Power") |
| **`rules`** | `card_id` | `TEXT` | `NOT NULL, FOREIGN KEY (cards.id)` | Karte, zu der der Regeltext gehört |
| | `rule_text` | `TEXT` | `NOT NULL` | Der vollständige Regeltext |

---

### 4. Verbindungstabellen (N-zu-N Beziehungen)

Diese Tabellen lösen Viele-zu-Viele-Beziehungen auf.

| Tabelle | Spalte | Datentyp | Constraints | Beschreibung |
| :--- | :--- | :--- | :--- | :--- |
| **`card_types`** | `card_id` | `TEXT` | `PRIMARY KEY, FOREIGN KEY (cards.id)` | Verknüpft eine Karte mit einem Typ |
| | `type_id` | `INTEGER` | `PRIMARY KEY, FOREIGN KEY (types.id)` | |
| **`card_subtypes`** | `card_id` | `TEXT` | `PRIMARY KEY, FOREIGN KEY (cards.id)` | Verknüpft eine Karte mit einem Untertyp |
| | `subtype_id` | `INTEGER` | `PRIMARY KEY, FOREIGN KEY (subtypes.id)` | |
| **`card_weaknesses`** | `card_id` | `TEXT` | `PRIMARY KEY, FOREIGN KEY (cards.id)` | Verknüpft eine Karte mit einer Schwäche |
| | `type_id` | `INTEGER` | `PRIMARY KEY, FOREIGN KEY (types.id)` | |
| | `value` | `INTEGER` | | Wert der Schwäche (z.B. 2 für "x2") |
| **`card_resistances`** | `card_id` | `TEXT` | `PRIMARY KEY, FOREIGN KEY (cards.id)` | Verknüpft eine Karte mit einer Resistenz |
| | `type_id` | `INTEGER` | `PRIMARY KEY, FOREIGN KEY (types.id)` | |
| | `value` | `INTEGER` | | Wert der Resistenz (z.B. -30) |