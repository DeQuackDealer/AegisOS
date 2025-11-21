
#!/bin/bash

# Aegis OS Freemium - XFCE Desktop Environment
# X11 initialization script

# Set environment variables
export XDG_CURRENT_DESKTOP=XFCE
export XDG_SESSION_DESKTOP=xfce
export DESKTOP_SESSION=xfce

# Apply gaming optimizations on desktop start
/usr/local/bin/aegis-gaming-optimizer &

# Start XFCE session
exec startxfce4
