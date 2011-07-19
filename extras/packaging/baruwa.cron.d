#
# Baruwa
#

# runs every 3 mins to update mailq stats
*/3 * * * * root baruwa-admin queuestats >/dev/null 2>&1
1 0 * * * root baruwa-admin sendquarantinereports >/dev/null