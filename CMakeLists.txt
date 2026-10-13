# fxlive's two hosts, built from an octabam checkout's sources into that
# checkout's out/fxlive/build (the Makefile configures it; octabam.py names
# the binaries):
#
#   dsp_host_stream  the checkout's tools/harness/dsp_host/dsp_host.cpp with
#                    patches/dsp_host-stream.patch applied (-stream: blocks
#                    over stdin and stdout). Patched at build time, so a
#                    branch that changes dsp_host.cpp gets its own host, and
#                    a patch that no longer applies stops the build.
#   ot_cf_host       cf_host.cpp, linked against the checkout's ot_machine.
#
# Both link the checkout's vendored cores through its own ot_emu project,
# added EXCLUDE_FROM_ALL so only what these two need is built.
cmake_minimum_required(VERSION 3.16)
project(fxlive CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
	set(CMAKE_BUILD_TYPE Release)
endif()

if(NOT OCTABAM OR NOT EXISTS "${OCTABAM}/tools/emu/ot_emu/CMakeLists.txt")
	message(FATAL_ERROR "fxlive: set -DOCTABAM=<octabam checkout> (got '${OCTABAM}')")
endif()

add_subdirectory("${OCTABAM}/tools/emu/ot_emu" ot_emu EXCLUDE_FROM_ALL)

find_program(PATCH patch REQUIRED)
set(DSP_HOST_SRC "${OCTABAM}/tools/harness/dsp_host/dsp_host.cpp")
set(DSP_HOST_PATCH "${CMAKE_CURRENT_SOURCE_DIR}/patches/dsp_host-stream.patch")
set(DSP_HOST_OUT "${CMAKE_CURRENT_BINARY_DIR}/dsp_host_stream.cpp")
add_custom_command(
	OUTPUT "${DSP_HOST_OUT}"
	COMMAND "${PATCH}" --fuzz=0 --silent -o "${DSP_HOST_OUT}.tmp" "${DSP_HOST_SRC}" "${DSP_HOST_PATCH}"
	COMMAND ${CMAKE_COMMAND} -E rename "${DSP_HOST_OUT}.tmp" "${DSP_HOST_OUT}"
	DEPENDS "${DSP_HOST_SRC}" "${DSP_HOST_PATCH}"
	COMMENT "fxlive: applying dsp_host-stream.patch to ${DSP_HOST_SRC}"
	VERBATIM)

add_executable(dsp_host_stream "${DSP_HOST_OUT}")
target_include_directories(dsp_host_stream PRIVATE "${OCTABAM}/vendor/dsp56300/source")
target_link_libraries(dsp_host_stream PRIVATE dsp56kEmu)

add_executable(ot_cf_host cf_host.cpp)
target_link_libraries(ot_cf_host PRIVATE ot_machine)
