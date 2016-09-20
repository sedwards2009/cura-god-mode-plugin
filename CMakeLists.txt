project(CuraGodModePlugin NONE)

cmake_minimum_required(VERSION 3.0.0)

install(FILES
    README.md
    DESTINATION lib/cura/plugins/GodMode
)

install(DIRECTORY src/GodMode
        DESTINATION lib/cura/plugins
        PATTERN "ExampleScript.py")

