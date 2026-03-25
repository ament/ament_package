# copied from ament_package/template/prefix_level/setup.fish

# Determine prefix from this script's location at runtime.
# 'status -f' gives the path of the currently sourced file in fish.
set -l AMENT_CURRENT_PREFIX (builtin realpath (dirname (status -f)))

# trace output
if test -n "$AMENT_TRACE_SETUP_FILES"
    echo "# source \"$AMENT_CURRENT_PREFIX/local_setup.fish\""
end

# Build ordered prefixes (same order as setup.sh.in) for overlay workspaces.
# Keep dedup inline: fish functions can't update caller local vars.
set -l _UNIQUE_PREFIX_PATH
set -l _parent_index \
    "$AMENT_CURRENT_PREFIX/share/ament_index/resource_index/parent_prefix_path"

if test -d "$_parent_index"
    for _resource in (command ls "$_parent_index" 2>/dev/null | command sort)
        read -z _content < "$_parent_index/$_resource" 2>/dev/null; or set _content ""
        set -l _paths (string split ":" -- "$_content")
        # Reverse the list (similar to setup.sh)
        set -l _reversed
        for _p in $_paths
            if test "$_p" = "{prefix}"
                set _p "$AMENT_CURRENT_PREFIX"
            end
            set _reversed "$_p" $_reversed
        end
        for _p in $_reversed
            if not contains -- "$_p" $_UNIQUE_PREFIX_PATH
                set -a _UNIQUE_PREFIX_PATH "$_p"
            end
        end
    end
end

# Always include the current prefix last (highest priority).
if not contains -- "$AMENT_CURRENT_PREFIX" $_UNIQUE_PREFIX_PATH
    set -a _UNIQUE_PREFIX_PATH "$AMENT_CURRENT_PREFIX"
end

# Source local_setup.fish for each prefix in order.
for _prefix_path in $_UNIQUE_PREFIX_PATH
    set -gx AMENT_CURRENT_PREFIX "$_prefix_path"
    if test -f "$_prefix_path/local_setup.fish"
        if test -n "$AMENT_TRACE_SETUP_FILES"
            echo "# source \"$_prefix_path/local_setup.fish\""
        end
        source "$_prefix_path/local_setup.fish"
    end
end

set -e AMENT_CURRENT_PREFIX
set -e _UNIQUE_PREFIX_PATH
set -e _parent_index
