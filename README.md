# Flame community names

Public text feed for the Arab Flame VRChat world. Names originate from the designated Flame Discord community channel. No Discord credentials, user IDs, or message IDs are included in this repository or the public feed.

The existing hosted Flame VIP service imports complete channel history and supports owner-only `/flame-remove name` and `/flame-restore name` commands. This repository publishes its validated snapshot through GitHub Pages so VRChat can read it using a default trusted domain.

## Enable publishing

Open **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**, then run **Actions → Publish Flame community names → Run workflow**.

The short publishing workflow checks for changes every five minutes. It uses GitHub's built-in ephemeral workflow token; no Discord bot token or personal access token is required here. A failed or incomplete source check retains the previous published names.

Scheduled jobs may be delayed or dropped by GitHub, and are disabled after 60 days without repository activity. If updates stop, check the Actions tab and re-enable the schedule. This publisher does not maintain a Discord Gateway connection or establish a green Online status for the bot.

The source service checks the channel on demand. Deleting a name with `/flame-remove` blocks that name durably; adding it again to the channel does not bypass that block. `/flame-restore` allows it again.
