# Connection parameters and authentication

The Teradata Jupyter SQL kernel wraps the Teradata SQL Driver; parameter names mirror the [Teradata JDBC Driver connection parameters](http://developer.teradata.com/doc/connectivity/jdbc/reference/current/jdbcug_chapter_2.html).

## Minimum viable connection

```
%addconnect name=prod, user=dbc, host=td.example.com
%connect prod
```

You will be prompted for the password on first connect. No password is ever stored in the notebook.

## Common connection parameters

| Parameter | Default | Description |
|---|---|---|
| `name` | *(required)* | Connection label used by `%connect`. |
| `host` | *(required)* | Hostname or IP of the Teradata system. |
| `user` | prompt | Username. If omitted, `%connect` prompts. |
| `database` | *(none)* | Default database set after connect. |
| `dbs_port` | `1025` | Teradata port. |
| `logmech` | `TD2` | Auth method: `TD2`, `LDAP`, `KRB5`, `BROWSER`, `TDNEGO`. Case-insensitive. |
| `logdata` | *(none)* | Extra auth data for the chosen `logmech`. |
| `account` | *(none)* | Teradata account string. |
| `encryptdata` | `true` | Encrypt data between driver and DB. Leave enabled. |
| `cop` | `true` | Enable COP discovery. |
| `coplast` | `false` | Control last-COP lookup behavior. |
| `sip_support` | `true` | Use StatementInfo parcel. |

## SSL / TLS

| Parameter | Default | Description |
|---|---|---|
| `sslmode` | `PREFER` | `DISABLE` / `ALLOW` / `PREFER` / `REQUIRE` / `VERIFY-CA` / `VERIFY-FULL`. |
| `sslca` | *(none)* | Path to a PEM file with CA certs. Required for `VERIFY-CA` / `VERIFY-FULL`. |
| `sslcapath` | *(none)* | Directory of PEM files (only `.pem` files are used). |

## Authentication mechanisms (`logmech`)

- `TD2` — classic Teradata user/password (default).
- `LDAP` — corporate directory auth.
- `KRB5` — Kerberos (use `logdata` for principal info if needed).
- `BROWSER` — browser-based SSO (macOS/Windows). The driver pops a browser window for auth.
- `TDNEGO` — server negotiates the mechanism.

## Examples

### LDAP

```
%addconnect name=corp, host=td.example.com, user=alice, logmech=LDAP
```

### Browser SSO

```
%addconnect name=sso, host=td.example.com, logmech=BROWSER
```

### Mutual-TLS with server cert verification

```
%addconnect name=secure, host=td.example.com, user=dbc, sslmode=VERIFY-FULL, sslca=/etc/ssl/td-ca.pem
```

## Troubleshooting

- **"Hostname not resolved"** — check VPN / DNS. Try `nslookup <host>` outside JupyterLab.
- **"Logon failed"** on a previously-working system — password may have rotated; re-run `%connect <name>` to re-prompt.
- **Browser SSO hangs** — a browser window must be able to reach the identity provider from the machine running JupyterLab, not the remote server.
- **SSL verify errors** — double-check the `sslca` PEM includes the issuing CA chain, not just the leaf cert.
- **Parameters not recognized** — any unknown parameter is passed through to the driver. Typos in parameter names do *not* error; they're silently forwarded. If behavior is off, re-check spelling.
