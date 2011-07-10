# baruwa - 1.1.0
#
# runs every 3 mins to update mailq stats

*/3 * * * * root baruwa-admin queuestats 2>/dev/null