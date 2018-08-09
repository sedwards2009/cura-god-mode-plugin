project(CuraGodModePlugin NONE)

cmake_minimum_required(VERSION 3.0.0)

install(FILES
    README.md
    DESTINATION lib${LIB_SUFFIX}/cura/plugins/GodMode
)

install(DIRECTORY src/GodMode
    DESTINATION lib${LIB_SUFFIX}/cura/plugins
    PATTERN
)
