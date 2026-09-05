# Bug log — Iris Classifier (CodeAlpha Task 3)

A record of every bug hit while wiring the Flask app together, in the order they came up. Kept for two reasons: so the fix doesn't get forgotten, and so the *pattern* behind each one is easier to recognize next time.

---

## 1. Jinja `block 'content' defined twice`

**Symptom:** `jinja2.exceptions.TemplateAssertionError: block 'content' defined twice`, pointing at `base.html` even though only one `{% block content %}` existed in the visible page markup.

**Cause:** An HTML comment (`<!-- ... -->`) in `base.html` contained the literal text `{% block content %}{% endblock %}` inside its explanatory notes. Jinja parses `{% %}` tags anywhere in the raw file — it has no concept of an HTML comment, since HTML comments are only hidden by the *browser*, after Jinja has already run. So Jinja saw two real block definitions: one inside the comment, one in the actual markup.

**Fix:** Reworded the comment so it no longer contained literal `{% %}` syntax.

**Tip:** For notes about templating logic, use a Jinja comment `{# ... #}` instead of an HTML comment `<!-- ... -->` — Jinja comments are genuinely invisible to the template engine. Save `<!-- -->` for notes about the resulting HTML.

---

## 2. `retrain()` called on every prediction

**Symptom:** No error — just a design flaw. Every `/predict` request retrained the model before returning a result, even though no new feedback existed yet.

**Cause:** `retrain()` was called unconditionally inside the `/predict` route instead of only after new feedback was recorded.

**Fix:** Moved the `retrain()` call into `add_user_feedback()`, after the database `UPDATE`, so it only runs when there's actually new labeled data.

**Tip:** Retraining is expensive and should be triggered by *new data arriving*, not by *someone using the app*. In production this would typically move to a background job or scheduled task instead of running inline in a request at all.

---

## 3. Missing route to *display* the feedback form

**Symptom:** No way to reach `feedback.html` — clicking a "correct this" link would 404.

**Cause:** The only `/feedback` route was a `POST` handler that *processed* a submission. Nothing existed to render the form itself for a given prediction.

**Fix:** Added `GET /feedback/<int:prediction_id>`, which looks up the stored prediction by id and renders `feedback.html` with it. The existing `POST /feedback` stayed as the form's submit target.

**Tip:** GET = "show me a page" (no side effects). POST = "do something / change data." A feature usually needs both a route to *display* something and a separate route to *act* on it.

---

## 4. `data_logger.py` — SQL syntax errors in `CREATE TABLE`

**Symptom:** Would raise `sqlite3.OperationalError` on table creation.

**Cause:** `CREAT TABLE` (typo for `CREATE`), and a missing comma between `DEFAULT CURRENT_TIMESTAMP` and the next column definition.

**Fix:** Corrected the keyword and added the missing comma.

**Tip:** SQL written as a multi-line Python string doesn't get syntax-checked until it actually runs — a quick read-through of raw SQL strings before running them catches this class of bug early.

---

## 5. Table name mismatch: `inferences` vs `inference_log`

**Symptom:** `sqlite3.OperationalError: no such table`.

**Cause:** `CREATE TABLE inferences (...)` but `INSERT INTO inference_log (...)` — two different names used for what was meant to be the same table.

**Fix:** Used `inferences` consistently everywhere.

**Tip:** Table/column names are just strings to the database — nothing catches a mismatch until the failing query runs. Worth defining these names once (e.g. as constants) if they're referenced in multiple files.

---

## 6. `predict()` returning a numpy array instead of a plain value

**Symptom:** The predicted species stored/displayed as `['setosa']` instead of `setosa`.

**Cause:** `pipeline.predict(...)` returns an array (even for one row); the code stored/returned the whole array instead of its first element.

**Fix:** `prediction = pipeline.predict(features_df)[0]`.

**Tip:** scikit-learn's `.predict()` always returns an array-like, even for a single input row — get in the habit of indexing `[0]` when predicting one row at a time.

---

## 7. Inconsistent import paths (`from data_logger import ...` vs `from src.data_logger import ...`)

**Symptom:** `ModuleNotFoundError` depending on where the script was run from.

**Cause:** Some files inside `src/` imported sibling modules with a flat import (`from data_logger import ...`), while `app.py` imported the whole thing as a package (`from src.predict import predict`). These two styles assume different working directories.

**Fix:** Standardized on `from src.<module> import <name>` everywhere, matching how `app.py` treats `src` as a package.

**Tip:** Pick one import style for the whole project and stick to it — mixing "flat" and "package" imports is one of the most common early Python project bugs.

---

## 8. `retrain.py` — several stacked bugs

- `from model import cross_validation` → wrong path, should be `from src.model import cross_validation` (same issue as #7).
- `SELECT * FROM infrences` → typo, should be `inferences`.
- `pd.concat(old_data, new_data, ...)` → wrong signature; `pd.concat()` takes a **list** of frames: `pd.concat([old_data, new_data], ...)`.
- Selecting a `Species` column that didn't exist in the `inferences` table (the real column was `user_feedback`, aliased to match on read: `SELECT ... , user_feedback AS Species ...`).
- `len(new_data) % 20 == 0` was `True` even at `0` rows (since `0 % 20 == 0`) — retraining would fire with zero new data. Fixed with `len(new_data) > 0 and len(new_data) % 20 == 0`.
- Database connection never closed in one branch.

**Tip:** When training on user feedback, always retrain on the **human-corrected label**, not the model's own (possibly wrong) prediction — otherwise the model just reinforces its own mistakes.

---

## 9. Hardcoded `'model_feedback.db'` repeated across files

**Symptom:** Not a bug yet, but a maintenance risk — the same literal string typed in three different files.

**Fix:** Centralized in `config.py`:
```python
DB_NAME = os.environ.get('DB_NAME', 'model_feedback.db')
```
and imported wherever needed: `from src.config import DB_NAME`.

**Tip:** `load_dotenv()` only needs to run once, in `config.py` — Python caches imported modules, so every other file importing `DB_NAME` reuses the already-loaded value without re-reading `.env`.

---

## 10. `INSERT` statement — mismatched placeholder/value count

**Symptom:** `sqlite3.ProgrammingError: Incorrect number of bindings supplied`.

**Cause:** SQL listed 5 columns and 5 `?` placeholders, but the Python tuple passed 6 values (an extra `user_feedback` that isn't known at insert time).

**Fix:** Dropped `user_feedback` from the insert — it gets added later via the feedback `UPDATE`, not at prediction time.

**Tip:** The number of `?` placeholders, the number of listed columns, and the number of values in the tuple all have to match exactly — a good habit is counting all three before running the query.

---

## 11. The recurring "wrong shape of data passed downstream" bug (several rounds)

This one showed up repeatedly, in slightly different forms, and is worth calling out as *one* underlying lesson rather than several separate bugs:

- **`{ }` instead of `[ ]`** in `app.py` created a Python **set**, not a list — sets don't preserve order and silently drop duplicate values, which would corrupt which measurement goes to which model feature.
- **DataFrame with no column names**, passed to a `ColumnTransformer` fit on named columns → `TypeError: 'NoneType' object is not iterable`. Fixed by building the DataFrame with explicit `columns=[...]` matching training-time names.
- **A DataFrame passed all the way into `accumulating_new_data()`**, which expected a plain list/dict → `features[0]` raised `KeyError: 0` (DataFrames don't support pure positional integer indexing like that), and `features['col']` returned a **pandas Series**, not a scalar → `sqlite3.ProgrammingError: type 'Series' is not supported`.
- **A DataFrame wrapped in another list** (`pd.DataFrame([already_a_dataframe])`) → `ValueError: Must pass 2-d input. shape=(1, 1, 4)` — the extra list added an unwanted third dimension.

**Root cause common to all of the above:** the same variable was passed through multiple functions that each expected a *different shape* of data (list, dict, DataFrame), without a clear boundary for where one shape gets converted into another.

**Fix / pattern adopted:**
- `app.py` builds a plain **dict** of raw form values — no pandas involved.
- `predict.py` is the **only** place that converts that dict into a DataFrame, and only for the single line that calls the model (`pipeline.predict(...)`). It keeps the original dict, under its own variable, to pass on unchanged.
- `data_logger.py` reads the dict by key (`features['SepalLengthCm']`) — never touches a DataFrame.

**Tip going forward:** for every function, ask "does this need *named* values (dict/DataFrame) or *ordered* values (list)?" — and only convert between the two at the exact boundary where the next function actually requires the other shape. Don't convert earlier than necessary, and don't let a converted copy silently overwrite the original variable name.

---
## 12. Flash messages appearing to "never disappear"

**Symptom:** After adding an auto-dismiss timer, messages still looked stuck on screen indefinitely.

**Likely causes (in order of likelihood, not fully confirmed):**
- **Browser caching** — the terminal log showed `304 Not Modified` for `style.css`, meaning the browser was reusing a cached copy instead of loading the updated file. A hard refresh (`Ctrl+Shift+R`) or an Incognito window rules this out.
- Possible Flask-side cause still to check: a flash message re-appearing on every page load (rather than one message failing to fade) would look identical to "never disappears" — this points at something calling `flash()` unconditionally, or a session/`SECRET_KEY` issue, rather than a front-end bug at all.

**Fix applied:** Replaced the JavaScript-based fade (which depends on the script actually loading and running) with a **pure CSS `@keyframes` animation** on `.flash` itself — appear, hold ~3s, fade out, `animation-fill-mode: forwards` to stay hidden. This removes JS entirely from the equation, so a stale-cache or script-loading issue can't be the cause anymore.

**Tip:** When a fix "doesn't work" after being applied correctly, hard-refresh or test in an Incognito/Private window before assuming the code is wrong — cached CSS/JS is one of the most common reasons a correct fix appears to do nothing.

---

## General lessons that came up more than once

- **Read the traceback from the bottom up** — the last few lines show the actual error and the exact file/line it happened on; everything above is the chain of calls that led there.
- **A caught exception (`except Exception as e: flash(...)`) hides the traceback.** Temporarily commenting out the `try/except` (with `debug=True`) surfaces the real error and exact line — much faster than guessing from a one-line flash message.
- **Restart the server after every code change.** Flask's reloader usually catches this automatically, but if in doubt, stop (`Ctrl+C`) and start again.
- **Paste the actual current file, not a memory of what it should contain**, when debugging — several rounds in this project went in circles because the fix was suggested for one version of a file while a different version was actually saved on disk.
