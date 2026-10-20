#!/usr/bin/env sh

# SPDX-FileCopyrightText: 2023 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# SPDX-FileContributor: Marcus Funch
#
# This script:
# 1. Install Chromium
# 2. Add a Chromium policy that:
#    - prevents Chromium from asking if it should be default browser and about browser metrics
#    - prevents the user logging in to the browser
#    - disables the remember password prompt feature.

# DEVELOPER NOTES:

set -ex

if get_os2borgerpc_config os2_product | grep --quiet kiosk; then
  echo "Dette script er ikke designet til at blive anvendt på en kiosk-maskine."
  exit 1
fi

ACTIVATE=$1
DEFAULT_SEARCH_ENGINE="$2"

# We refer to Chrome policies here because we're trying to share the policies between Chrome and Chromium
CHROME_POLICIES_PATH="/etc/opt/chrome/policies"
CHROMIUM_POLICIES_PATH="/var/snap/chromium/current/policies"
USER_CLEANUP="/usr/share/os2borgerpc/bin/user-cleanup.bash"
SKELETON=".skjult"
BROWSER_HOME="/home/$SKELETON/snap/chromium/common/chromium/"

### START SHARED BLOCK BETWEEN CHROMIUM BROWSERS: CHROMIUM, CHROME ###
setup_policies() {
  #
  # DEVELOPER NOTES:
  #
  # > POLICIES:
  #
  # The policies we set and why
  #
  # Lockdown:
  # AutofillAddressEnabled: Disable Autofill of addresses
  # AutofillCreditCardEnabled: Disable Autofill of payment methods
  # BrowserAddPersonEnabled: Make it impossible to add a new Profile. Doesn't lock down editing a Profile, but it gets some of the way.
  # BrowserSignin: Disable sync/login with own google account
  # DeveloperToolsAvailability: Disables access to developer tools, where someone could make changes to a website
  # EnableMediaRouter: Disable Chrome Cast support
  # ExtensionInstallBlocklist: With the argument * it blocks installing any extension
  # ForceEphemeralProfiles: Clear Profiles on browser close automatically, for privacy reasons
  # PaymentMethodQueryEnabled: Prevent websites from checking if the user has saved payment methods
  #
  # Various:
  # BrowserGuestModeEnabled: Allow people to start a guest session, if they want, so history isn't even temporarily recorded. Not crucial.
  # BrowsingDataLifetime: Continuously remove all browsing data after 1 hour (the minimum possible),
  # except "cookies_and_other_site_data" and "password_signin",
  # because the visitor might be at the computer and still signed in to something.
  # DefaultBrowserSettingEnabled: Don't check if it's default browser. Irrelevant for visitors, and maybe you want Firefox as default.
  # MetricsReportingEnabled: Disable some of Googles metrics, for privacy reasons
  # PasswordManagerEnabled: Don't try to save passwords on a public machine used by many people
  # PrivacySandboxPromptEnabled: Don't prompt about enabling (some) ad tracking
  # PrivacySandboxSiteEnabledAdsEnabled: Disable (some) ad tracking

  # Additional info on the many policies that can be set:
  # https://support.google.com/chrome/a/answer/187202?hl=en
  #
  # Blocked URLs
  #
  # chrome://accessibility: It seems to have what's essentially a builtin keylogger?!
  # chrome://extensions: Extension settings can be changed here, and extensions enabled/disabled
  # chrome://flags: Experimental features can be enabled/disabled here.

  # Cleanup our previous policies if they're around (except the homepage)
  rm --force /etc/opt/chrome/policies/managed/os2borgerpc-default-hp.json /etc/opt/chrome/policies/managed/os2borgerpc-login.json

  # Create the new policies
  POLICY="/etc/opt/chrome/policies/managed/os2borgerpc-defaults.json"

  mkdir --parents "$(dirname "$POLICY")"

  # Ensure that the default pdf reader setting is correct to prevent the computer
  # from using Chrome as a pdf reader
  GLOBAL_MIME_FILE="/etc/xdg/mimeapps.list"
  if [ -f "$GLOBAL_MIME_FILE" ]; then
    sed --in-place "s@/usr/share/applications/@@" $GLOBAL_MIME_FILE
  fi

  cat > "$POLICY" << END
{
    "AutofillAddressEnabled": false,
    "AutofillCreditCardEnabled": false,
    "BrowserAddPersonEnabled": false,
    "BrowserGuestModeEnabled": true,
    "BrowserSignin": 0,
    "BrowsingDataLifetime": [
      {
        "data_types": [
          "autofill",
          "browsing_history",
          "cached_images_and_files",
          "download_history",
          "hosted_app_data",
          "site_settings"
        ],
        "time_to_live_in_hours": 1
      }
    ],
    "DefaultBrowserSettingEnabled": false,
    "DeveloperToolsAvailability": 2,
    "EnableMediaRouter": false,
    "ExtensionInstallBlocklist": [
      "*"
    ],
    "ForceEphemeralProfiles": true,
    "MetricsReportingEnabled": false,
    "PasswordManagerEnabled": false,
    "PaymentMethodQueryEnabled": false,
    "PrivacySandboxPromptEnabled": false,
    "PrivacySandboxSiteEnabledAdsEnabled": false,
    "URLBlocklist": [
      "chrome://accessibility",
      "chrome://extensions",
      "chrome://flags"
    ]
}
END

  # This entire policy file is overwritten if you later run the script to change the homepage
  # We set it here too so all machines have a startpage set, to prevent someone from manually setting the homepage to
  # some malicious site
  HOMEPAGE_POLICY="/etc/opt/chrome/policies/managed/os2borgerpc-homepage.json"
  if [ ! -f $HOMEPAGE_POLICY ]; then
cat > "$HOMEPAGE_POLICY" <<- END
{
    "HomepageLocation": "https://borger.dk",
    "RestoreOnStartup": 4,
    "ShowHomeButton": true,
    "HomepageIsNewTabPage": false,
    "RestoreOnStartupURLs": [
        "https://borger.dk"
    ]
}
END
  fi

SEARCH_POLICY="/etc/opt/chrome/policies/managed/os2borgerpc-search-provider.json"

# DefaultSearchProviderEnabled: Default search is performed when a user enters non-URL text in the address bar. The default search provider can not be changed by a user.
# DefaultSearchProviderIconURL: Specifies the default search provider's favorite icon URL.
# DefaultSearchProviderName: Specifies the default search provider's name.
# DefaultSearchProviderSearchURL: Specifies the URL of the search provider used during a default search.
# DefaultSearchProviderSuggestURL: Specifies the URL of the search provider to provide search suggestions.
if [ "$DEFAULT_SEARCH_ENGINE" = "google" ]; then
  # Set the default search provider to Google, so Chrome stops asking every time
  # the browser is opened.
  # Chrome will default to using Google if we leave DefaultSearchProviderSearchURL
  # blank
  cat << EOF > "$SEARCH_POLICY"
{
    "DefaultSearchProviderEnabled": true,
    "DefaultSearchProviderSearchURL": ""
}
EOF
elif [ "$DEFAULT_SEARCH_ENGINE" = "ecosia" ]; then
  cat << EOF > $SEARCH_POLICY
{
    "DefaultSearchProviderEnabled": true,
    "DefaultSearchProviderName": "Ecosia",
    "DefaultSearchProviderKeyword": "ecosia",
    "DefaultSearchProviderSearchURL": "https://www.ecosia.org/search?q={searchTerms}&addon=chromegpo",
    "DefaultSearchProviderNewTabURL": "https://www.ecosia.org/newtab/?addon=chromegpo",
    "DefaultSearchProviderSuggestURL": "https://ac.ecosia.org/autocomplete?q={searchTerms}&type=list"
}
EOF
elif [ "$DEFAULT_SEARCH_ENGINE" = "qwant" ]; then
  cat << EOF > $SEARCH_POLICY
{
    "DefaultSearchProviderEnabled": true,
    "DefaultSearchProviderName": "Qwant",
    "DefaultSearchProviderKeyword": "qwant",
    "DefaultSearchProviderSearchURL": "https://www.qwant.com/?q={searchTerms}",
    "DefaultSearchProviderNewTabURL": "https://www.qwant.com",
    "DefaultSearchProviderSuggestURL": "https://api.qwant.com/api/suggest/?q={searchTerms}&type=web"
}
EOF
elif [ "$DEFAULT_SEARCH_ENGINE" = "startpage" ]; then
  cat << EOF > $SEARCH_POLICY
{
    "DefaultSearchProviderEnabled": true,
    "DefaultSearchProviderName": "StartPage",
    "DefaultSearchProviderKeyword": "startpage",
    "DefaultSearchProviderSearchURL": "https://www.startpage.com/sp/search?query={searchTerms}&cat=web&pl=chrome",
    "DefaultSearchProviderNewTabURL": "https://www.startpage.com",
    "DefaultSearchProviderSuggestURL": "https://www.startpage.com/osuggestions?q=%s"
  }
EOF
elif [ "$DEFAULT_SEARCH_ENGINE" = "duckduckgo" ]; then
  cat << EOF > $SEARCH_POLICY
{
    "DefaultSearchProviderEnabled": true,
    "DefaultSearchProviderName": "DuckDuckGo",
    "DefaultSearchProviderKeyword": "duckduckgo",
    "DefaultSearchProviderSearchURL": "https://duckduckgo.com/?q={searchTerms}",
    "DefaultSearchProviderNewTabURL": "https://www.duckduckgo.com",
    "DefaultSearchProviderSuggestURL": "https://duckduckgo.com/ac/?q={searchTerms}&type=list"
}
EOF
fi

}
### END SHARED BLOCK BETWEEN CHROMIUM BROWSERS: CHROMIUM, CHROME ###


if [ "$ACTIVATE" = "True" ]; then
  snap install chromium

  # NOTE: Create policies **after** snap install, as creating it before seems to interfere with the snap installation
  mkdir --parents "$(dirname $CHROMIUM_POLICIES_PATH)"
  ln --symbolic --force $CHROME_POLICIES_PATH $CHROMIUM_POLICIES_PATH

  setup_policies

  # 2026-08: Prevent popup on first run about a service agreement related to AVC:
  #          https://www.google.com/chrome/terms/
  #          Unfortunately it appears like there's no enterprise policy for this,
  #          yet, which would be better
  mkdir --parents "$BROWSER_HOME"
  touch "$BROWSER_HOME/EULA Accepted"

  # Alter user-cleanup.bash to prevent problems with chromium
  # This involves altering user-cleanup to not delete everything
  # under /tmp/, but only the user-owned files/directories
  # This is only necessary on 22.04 (20.04 is no longer supported)
  if lsb_release -d | grep --quiet 22; then
    sed --in-place "s@/tmp/\* /tmp/\.??\* @@" $USER_CLEANUP
    if ! grep --quiet "FILES_DIRS" $USER_CLEANUP; then
    cat << EOF >> $USER_CLEANUP

# Find all files/directories owned by user in the world-writable directories
FILES_DIRS=\$(find /tmp/ /var/tmp/ /var/crash/ /var/metrics/ /var/lock/ -user user)
rm --recursive --force /dev/shm/* /dev/shm/.??* \$FILES_DIRS
EOF
    else
      sed --in-place "s@find /var@find /tmp/ /var@" $USER_CLEANUP
    fi
  fi
else
  snap remove chromium
  # Remove chromium policies directory and symlink - removing the dir is significant
  rm --force --recursive $CHROMIUM_POLICIES_PATH "$BROWSER_HOME"
fi
