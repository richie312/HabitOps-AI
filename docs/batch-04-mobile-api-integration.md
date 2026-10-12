## MySQL Environment Setup — Raspberry Pi

### Environment

- MySQL version: 8.0.45
- Host: `192.168.1.50`
- Port: `3306`
- Database: `habitops`
- Application user: `habitops_app`
- Application host restriction: `192.168.1.8` (development PC)
- Docker container: `mysql`
- Persistent Docker volume: `mysql_ubuntu_rasp_device`
- Flask health endpoint: `GET /api/health`

### Database persistence

HabitOps AI must use the existing MySQL container and its persistent Docker volume. Never remove or recreate the volume as part of application deployment or troubleshooting.

The application must not use the MySQL root account. Use the dedicated `habitops_app` account with access restricted to the HabitOps database.

### Initial database provisioning

The database and application account are provisioned manually by an administrator. The following commands document the initial setup; do not execute them repeatedly without checking the existing state.

```sql
CREATE DATABASE habitops
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'habitops_app'@'192.168.1.8'
  IDENTIFIED BY '<SET_THE_SAME_PASSWORD_AS_BACKEND_ENV>';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX
ON habitops.*
TO 'habitops_app'@'192.168.1.8';
```

Replace the password placeholder with the application password configured in `backend/.env`. Never commit the actual password or include it in logs or documentation.

The account is restricted to the development PC's IP address. If the PC's IP changes, update the MySQL account host restriction deliberately rather than opening access to all hosts.

### Backend environment variables

Configure the following variables in `backend/.env`:

```dotenv
MYSQL_HOST=192.168.1.50
MYSQL_PORT=3306
MYSQL_DATABASE=habitops
MYSQL_USERNAME=habitops_app
MYSQL_PASSWORD=<YOUR_APPLICATION_PASSWORD>
```

The `.env` file must remain untracked by Git. Commit only `backend/.env.example` with placeholder values.

### Schema initialization

After confirming connectivity, initialize the HabitOps schema using the project's documented, idempotent schema initialization procedure. Create only HabitOps-specific tables for activities, vitals and GPS route points. Do not modify unrelated databases or tables.

### Verification requirements

1. Verify the application account can connect to the `habitops` database from the development PC.
2. Start Flask and call `GET /api/health`.
3. Verify that the health endpoint accurately reports database connectivity.
4. Create and retrieve a test activity and vital record through the API.
5. Verify GPS route coordinates are saved and retrieved correctly.
6. Restart Flask and confirm that the records remain in MySQL.
7. Reopen the mobile app and confirm that history and analytics retrieve the persisted records.

The Android application must communicate with Flask over the local network. It must never connect directly to MySQL or use `localhost` as the backend host on a physical Android device.

### Known diagnostic finding

The initial database connection failed because the `habitops` database and `habitops_app` account did not exist. They have since been created, and the user has confirmed successful setup. The Flask database health check and end-to-end persistence tests still need to be verified.

Do not claim integration acceptance until these runtime checks have passed.
