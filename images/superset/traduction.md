### SUMMARY
Update the french po file to apply the translation template. The current file has some weird translations and misses some keys from the template.

### ADDITIONAL INFORMATION

To get the new values from .pot template, I ran the following command : `msgmerge --update superset/translations/fr/LC_MESSAGES/messages.po superset/translations/messages.pot`

IMO, there is a huge work to adress on french translation. The same word can use multiple translation which can lead the user to confusion.
Few example
`rows` => `rangées` or ` lignes`
`dataset` => `ensemble de données` or `jeu de données` 

I suggest to define a single "admited" translation from now on and future evolution. Here is the list for the most common terms which needs consistency.

| Eng | French |
|--------|--------|
| `chart` | `graphique`|
| `dataset` | `jeu de données` |
| `semantic layer` | `couche sémantique` |
| `tag` | `etiquette`|
| `currency` | `devise` |
| `plugin` | `plugin` |
| `upload` | `charger` | 
| `layers` (in context of map) | `couche` | 
| `layers` (in context of annotation) | `couche` | 
| `email` | `mail` | 
| `table` (in contexte of database) | `table` | 
| `rows` | `lignes` | 
| `X-axis` | `axe X`| 
| `Y-axis` | `axe Y` |
| `folder` | `dossier` |
| `Genderify user terms` | `Non` | 
