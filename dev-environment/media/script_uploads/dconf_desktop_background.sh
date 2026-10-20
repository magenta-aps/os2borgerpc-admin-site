#!/usr/bin/env sh

# SPDX-FileCopyrightText: 2019 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# SPDX-FileContributor: Alexander Faithful, Marcus Funch

# SYNOPSIS
#    dconf_policy_desktop_background.sh [FILE] [PICTURE_OPTION]
#
# DESCRIPTION
#    This script changes and locks the desktop background for all users on the
#    system using a dconf lock.
#
#    It requires two parameters:
#    1. The path to the desktop background.
#    2. Picture options. The default in GNOME is "zoom".
#       Other picture options are: zoom, centered, stretched, spanned, wallpaper, scaled, none

set -x

if get_os2borgerpc_config os2_product | grep --quiet kiosk; then
  echo "Dette script er ikke designet til at blive anvendt på en kiosk-maskine."
  exit 1
fi

IMAGE_FILE=$1
IMAGE_FILE_DARK=$2
OPTION_VALUE=$3
POLICY_FILE="/etc/dconf/db/os2borgerpc.d/00-background"
POLICY_LOCK_FILE="/etc/dconf/db/os2borgerpc.d/locks/00-background"

# Delete the previous lock file (its name has changed)
rm --force /etc/dconf/db/os2borgerpc.d/locks/background

if [ -n "$IMAGE_FILE" ] && [ -f "$IMAGE_FILE" ]; then

	# Copy the new desktop background into the appropriate folder
	LOCAL_PATH="/usr/share/backgrounds/$(basename "$IMAGE_FILE")"
	cp "$IMAGE_FILE" "$LOCAL_PATH"

	cat > "$POLICY_FILE" <<-END
		[org/gnome/desktop/background]
		picture-uri='file://$LOCAL_PATH'
		picture-options='$OPTION_VALUE'
	END
	# Tell the system that the values of the dconf keys we've just set can no
	# longer be overridden by the user
	cat > "$POLICY_LOCK_FILE" <<-END
		/org/gnome/desktop/background/picture-uri
		/org/gnome/desktop/background/picture-options
	END

	if [ -n "$IMAGE_FILE_DARK" ] && [ -f "$IMAGE_FILE_DARK" ]; then
	  # Copy the dark mode desktop background into the appropriate folder
	  LOCAL_PATH_DARK="/usr/share/backgrounds/$(basename "$IMAGE_FILE_DARK")"
	  cp "$IMAGE_FILE_DARK" "$LOCAL_PATH_DARK"

	  # Update the above dconf files to also set the dark mode desktop background
	  echo "picture-uri-dark='file://$LOCAL_PATH_DARK'" >> "$POLICY_FILE"
	  echo "/org/gnome/desktop/background/picture-uri-dark" >> "$POLICY_LOCK_FILE"
	fi
else
	printf "Missing mandatory image file parameter. Exiting."
	exit 1
fi

# Incorporate all of the text files we've just created into the system's dconf databases
dconf update
