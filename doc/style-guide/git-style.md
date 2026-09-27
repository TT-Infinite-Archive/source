Git Style Guidelines
====================
For Git, we follow a set pattern for commit messages and branch names to keep the history organized and readable.
- - -
## Commit Messages ##
Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): summary
```

The **type** is one of:

| Type       | Use it for                                        |
| ---------- | ------------------------------------------------- |
| `feat`     | A new feature or gameplay change                  |
| `fix`      | A bug fix                                         |
| `perf`     | A performance improvement                         |
| `refactor` | A code change that doesn't change behavior        |
| `chore`    | Tooling, CI, dependencies, config and cleanup     |
| `docs`     | Documentation only                                |

The release notes are built from these types, so choose the one that matches the change.

The **scope** is the area of the game or repository the commit touches most, such as `parties`, `toon`, `coghq`, `ai`, `uberdog`, `launcher`, `docker` or `workflows`. Leave it out if no single area fits.

The **summary** should:
* Be entirely lower case, except for names and identifiers.
* Be in the present tense and imperative mood ("add", not "added" or "adds").
* Never end in punctuation.
* Keep the whole title under 100 characters.

If you add a description, separate it from the title with a blank line and explain *why* the change was made. If the commit addresses an issue, reference it at the end of the description, e.g. `Fixes #42`.

For example: ```fix(minigames): finish every cog thief pie track on cleanup``` or ```feat(parties): add the dance floor to the party catalog```

## Branch Naming ##
All branch names should:
* Be entirely lower case.
* Use **-** as a separator.
* Be categorized into one of the following groups:
    * wip
    * bugfix
    * test
    * enhancement
    * feature

For example: ```feature/parties``` or ```bugfix/toontorial``` or ```enhancement/fix-memory-leak```
