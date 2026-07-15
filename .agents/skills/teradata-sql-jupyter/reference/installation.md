# Installing and running the Teradata Jupyter SQL extensions

The Teradata Jupyter extensions give you:
- a **Teradata SQL kernel** (`teradatasql`) that runs SQL and `%magic` commands,
- a **Navigator** side panel for browsing databases/tables,
- a **Connection Manager** for managing connection profiles.

Landing page with downloads: https://teradata.github.io/jupyterextensions/
Sample notebooks: https://github.com/Teradata/jupyterextensions/tree/master/notebooks

There are two supported install paths. Pick one.

---

## Path A — Teradata Jupyter Docker image (recommended for trying it out)

A pre-built Docker image with JupyterLab and all Teradata extensions installed.

1. Pull the image (check the landing page above for the current tag):

   ```bash
   docker pull teradata/jupyterlab-extensions:latest
   ```

2. Start the container, mounting a local folder where your notebooks live:

   ```bash
   docker run --rm -it \
     -p 8888:8888 \
     -v "$PWD":/home/jovyan/work \
     teradata/jupyterlab-extensions:latest
   ```

3. Open the URL printed in the terminal (starts with `http://127.0.0.1:8888/lab?token=...`).

4. In the JupyterLab launcher you should see a **Teradata SQL** kernel tile. Clicking it creates a new `.ipynb` with the `teradatasql` kernel.

**Verify install:** new notebook → first cell → `%lsmagic` → should list `%connect`, `%addconnect`, `%chart`, `%dataload`, `%history`, etc.

---

## Path B — Install into an existing JupyterLab

Requires Python 3.8+ and a recent JupyterLab (4.x).

1. Activate the Python environment where JupyterLab runs.

2. Install the kernel and extensions. Exact package names are on the landing page; typical command:

   ```bash
   pip install teradatasql teradatasqlalchemy
   pip install jupyterlab_teradatasql   # Teradata SQL kernel + extensions
   ```

3. Register the kernel if the installer didn't:

   ```bash
   python -m teradatasqlkernel install --user
   ```

4. Restart JupyterLab (full stop + start; `jupyter lab build` may be needed on older JupyterLab versions).

5. Launch JupyterLab:

   ```bash
   jupyter lab
   ```

   You should see a **Teradata SQL** tile in the launcher and a Teradata icon in the left sidebar (Navigator / Connection Manager).

---

## First-run checklist

Open a new **Teradata SQL** notebook and run:

```
%lsmagic
```

You should see the connection, chart, history, dataload, and help magics. Then:

```
%var systemName=<your-system>, user=<your-user>, host=<your-host>
%addconnect name=${systemName}, user=${user}, host=${host}
%connect ${systemName}
```

Enter the password when prompted. Then:

```
SELECT CURRENT_USER, DATABASE;
```

If you get a row back, you're good.

---

## Headless execution (CI / scripted runs)

Run a notebook without opening JupyterLab:

```bash
jupyter nbconvert --to notebook --execute my.ipynb \
    --ExecutePreprocessor.kernel_name=teradatasql \
    --ExecutePreprocessor.timeout=600
```

This requires a connection profile already defined on the system (through `%addconnect` in a previous interactive session, or via a pre-seeded `~/.teradata` config, depending on the extension version). Password prompts don't work headlessly — use `KRB5`, `LDAP` with `logdata`, or a pre-authenticated browser SSO session.

---

## Common install problems

| Symptom | Likely cause | Fix |
|---|---|---|
| No **Teradata SQL** tile in the launcher | Kernel not registered | `jupyter kernelspec list` — if `teradatasql` missing, rerun the kernel install step. |
| Launcher tile exists but magics fail with "unknown command" | JupyterLab extension not installed / not built | `jupyter labextension list` should show the Teradata extension. Restart JupyterLab, run `jupyter lab build` on older versions. |
| No Teradata icon in the left sidebar | Labextension disabled | `jupyter labextension enable @teradata/...` then restart. |
| `%connect` hangs with `BROWSER` logmech | Browser can't reach the IdP from this machine | Run JupyterLab on a desktop that can open browser windows, or switch to `LDAP`/`KRB5`/`TD2`. |
| `%dataload` can't find the CSV | Relative path is relative to the JupyterLab working directory, not the notebook | Use a path like `notebooks/sql/data/foo.csv` (from the working directory), or an absolute path. |
| SSL verify errors | Missing CA file or wrong chain | Set `sslca=/path/to/ca.pem` on `%addconnect`; start with `sslmode=REQUIRE` to isolate the issue, then upgrade to `VERIFY-CA` / `VERIFY-FULL`. |
| Kernel present, but SQL returns nothing | Wrong active connection or database | `%lsconnect` to confirm which is `*Connected`; `%currentdb` to confirm the database. |

## Getting help

- Community forum: https://community.teradata.com/t5/Teradata-SQL-Extension-for/bd-p/Jupyter
- Paid support: https://access.teradata.com/
- Issue tracker and sample notebooks: https://github.com/Teradata/jupyterextensions
