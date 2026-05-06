# ntfy-PAM Auth
Secure push-based 2FA for SSH, Sudo, etc.

## 1. Deploy ntfy (Docker)
```bash
# Start server
docker-compose up -d

# Configure auth
docker exec -it ntfy ntfy user add --role=admin admin
docker exec -it ntfy ntfy user change-pass admin
docker exec -it ntfy ntfy token add admin
docker exec -it ntfy ntfy access '*' 'AuthBot_Check' write-only
```

## 2. Configure App
Rename `config.json.example` to `config.json` and update:
```json
{
    "ntfy_token": "tk_...",
    "public_url": "https://your-domain.com",
    "topic_url": "https://your-domain.com/AuthBot",
    "response_url": "https://your-domain.com/AuthBot_Check",
    "project_path": "/path/to/your/Auth/directory"
}
```

## 3. Enable PAM
Add to `/etc/pam.d/sshd` or `/etc/pam.d/sudo`:
```bash
auth required pam_exec.so expose_authtok /path/to/pam_ssh_ntfy.py
```

## How it works
1. **Trigger**: Service calls script.
2. **Push**: Notification sent to phone with Approve/Deny buttons.
3. **Reply**: Phone posts response to `AuthBot_Check` (anonymous write).
4. **Grant**: Script polls response and exits 0 on success.
