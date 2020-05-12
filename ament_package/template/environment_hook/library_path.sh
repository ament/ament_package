# copied from ament_package/template/environment_hook/library_path.sh

# detect if running on Darwin platform
_UNAME=`uname -s`
_IS_DARWIN=0
if [ "$_UNAME" = "Darwin" ]; then
  _IS_DARWIN=1
fi
unset _UNAME

# Collect machine architecture triplet for libraries using GNU install dirs
_MULTIARCH_TRIPLET=`gcc -dumpmachine OUTPUT_VARIABLE MULTIARCH_TRIPLET OUTPUT_STRIP_TRAILING_WHITESPACE`

if [ $_IS_DARWIN -eq 0 ]; then
  ament_prepend_unique_value LD_LIBRARY_PATH "$AMENT_CURRENT_PREFIX/lib"
  ament_prepend_unique_value LD_LIBRARY_PATH "$AMENT_CURRENT_PREFIX/lib/$MULTIARCH_TRIPLET"
else
  ament_prepend_unique_value DYLD_LIBRARY_PATH "$AMENT_CURRENT_PREFIX/lib"
  ament_prepend_unique_value DYLD_LIBRARY_PATH "$AMENT_CURRENT_PREFIX/lib/$MULTIARCH_TRIPLET"
fi
unset _MULTIARCH_TRIPLET
unset _IS_DARWIN
