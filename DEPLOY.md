# Deploy Rapido (Meta90)

## 1) Variables minimas en Render (Web Service)

- `APP_ENV=production`
- `SECRET_KEY=<clave_larga_unica>`
- `DATABASE_URL=<postgresql://...>`
- `COOKIE_SECURE=1`
- `COOKIE_SAMESITE=Lax`

OAuth opcional (si usas botones sociales):

- Google:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `GOOGLE_REDIRECT_URI` (vacio en produccion)
- Facebook:
  - `FACEBOOK_APP_ID`
  - `FACEBOOK_APP_SECRET`
  - `FACEBOOK_GRAPH_VERSION` (ej. `v25.0`)
- Microsoft:
  - `MICROSOFT_CLIENT_ID`
  - `MICROSOFT_CLIENT_SECRET`
  - `MICROSOFT_TENANT=common`

## 2) Callbacks OAuth en proveedores

- Google Redirect URI:
  - `https://meta90-app.onrender.com/auth/google/callback`
- Facebook Valid OAuth Redirect URI:
  - `https://meta90-app.onrender.com/auth/facebook/callback`
- Microsoft Redirect URI (Web):
  - `https://meta90-app.onrender.com/auth/microsoft/callback`

## 3) Verificacion local antes de subir

```powershell
scripts\predeploy_check.bat
```

## 4) Deploy

1. `git push origin main`
2. Render -> `Manual Deploy` -> `Deploy latest commit`
3. Validar:
   - `https://meta90-app.onrender.com/health`
   - login normal
   - login Google/Facebook/Microsoft (si aplica)

## 5) Rotacion de secretos (si hubo exposicion)

Rotar y actualizar en Render:

- `DATABASE_URL` (password de Postgres)
- `GOOGLE_CLIENT_SECRET`
- `FACEBOOK_APP_SECRET`
- `TWILIO_AUTH_TOKEN`
- `SECRET_KEY`
