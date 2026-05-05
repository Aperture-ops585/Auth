# Secure Push Authentication with ntfy & PAM

A second-factor push authentication system for Linux services (SSH, Sudo, etc.) using a self-hosted ntfy server.

---

### Project Structure
- `config.json`: Centralized configuration (Token, URLs, Tags).
- `ntfy_auth.py`: Library for sending formatted push notifications.
- `pam_ssh_ntfy.py`: The PAM execution script (sends push & polls for response).
- `README.md`: This setup guide.
- `NGINX_SETUP.md`: Guide for local Nginx + SSL setup.

---

### Phase 1: ntfy Server Configuration (Docker)

1. **Start ntfy** with port 2586 and volumes for persistence.
2. **Enable Authentication** in `server.yml`:
   ```yaml
   auth-file: "/var/lib/ntfy/user.db"
   auth-default-access: "deny-all"
   ```
3. **Grant Permissions**:
   ```bash
   # Create admin user & generate token
   ntfy user add --role=admin my_auth_user
   ntfy token add my_auth_user
   
   # Allow anonymous WRITE-ONLY access to the response topic
   # (Needed for phones to reply without embedding tokens in buttons)
   ntfy access '*' 'AuthBot_Check' write-only
   ```

---

### Phase 2: Configuration (`config.json`)

Update your local credentials and URLs here:
```json
{
    "ntfy_token": "tk_...",
    "topic_url": "https://authctrl.duckdns.org/AuthBot",
    "response_url": "https://authctrl.duckdns.org/AuthBot_Check",
    "pam_script_path": "/home/aperture/Auth/pam_ssh_ntfy.py",
    "tags": "shield"
}
```

---

### Phase 3: The Authentication Flow

1. **Trigger**: A PAM-enabled service (like SSH) calls `pam_ssh_ntfy.py`.
2. **Challenge**: The script sends a push to your phone with "Approve" and "Deny" buttons.
3. **Response**: 
   - Tapping **Approve** POSTS `approved:<request_id>` to the `AuthBot_Check` topic.
   - This works anonymously because the topic is `write-only`.
4. **Verification**: 
   - The PAM script polls `AuthBot_Check` using the Bearer Token.
   - It matches the message against the active `request_id`.
   - **Exit Code 0** grants access; **Exit Code 1** denies it.

---

### Phase 4: Implementation (Linux PAM)

Add the following line to any file in `/etc/pam.d/` (e.g., `sshd`, `sudo`, `sddm`):

```text
auth required pam_exec.so expose_authtok /home/aperture/Auth/pam_ssh_ntfy.py
```

- **Ordering**: Place it **after** `@include common-auth` for 2FA behavior.
- **Service Awareness**: The script automatically detects the service name and displays it in the notification (e.g., "SUDO login attempt").
