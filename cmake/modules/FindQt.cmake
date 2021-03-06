# - Searches for Qt4 or Qt5.

# Copyright (C) 2001-2009 Kitware, Inc.
# Copyright (C) 2011 Collabora Ltd. <http://www.collabora.co.uk/>
# Copyright (C) 2011 Nokia Corporation
#
# Redistribution and use is allowed according to the terms of the BSD license.
# For details see the accompanying COPYING-CMAKE-SCRIPTS file.

IF(DESIRED_QT_VERSION MATCHES 5)
    # Qt5 was explicitly requested, so use its CMakeConfig instead of qmake which may not be at a global location
    find_package(Qt5Core QUIET)
    IF( Qt5Core_DIR )
        SET(QT5_INSTALLED TRUE)
    ENDIF()
ENDIF()

#Otherwise search for installed qmakes
IF(NOT QT5_INSTALLED)
    IF(NOT QT_QMAKE_EXECUTABLE)
        FIND_PROGRAM(QT_QMAKE_EXECUTABLE_FINDQT NAMES qmake qmake4 qmake-qt4 qmake5 qmake-qt5
            PATHS "${QT_SEARCH_PATH}/bin" "$ENV{QTDIR}/bin")
        SET(QT_QMAKE_EXECUTABLE ${QT_QMAKE_EXECUTABLE_FINDQT} CACHE PATH "Qt qmake program.")
    ENDIF()

    # now find qmake
    IF(QT_QMAKE_EXECUTABLE)
        EXEC_PROGRAM(${QT_QMAKE_EXECUTABLE} ARGS "-query QT_VERSION" OUTPUT_VARIABLE QTVERSION)
        IF(QTVERSION MATCHES "4.*")
            SET(QT4_INSTALLED TRUE)
        ENDIF()
        IF(QTVERSION MATCHES "5.*")
            SET(QT5_INSTALLED TRUE)
        ENDIF()
    ENDIF()
ENDIF()

IF(NOT DESIRED_QT_VERSION)
  IF(QT4_INSTALLED)
    SET(DESIRED_QT_VERSION 4 CACHE STRING "Pick a version of Qt to use: 4 or 5")
  ENDIF()
  IF(QT5_INSTALLED)
    SET(DESIRED_QT_VERSION 5 CACHE STRING "Pick a version of Qt to use: 4 or 5")
  ENDIF()
ENDIF()

IF(DESIRED_QT_VERSION MATCHES 4)
  SET(Qt4_FIND_REQUIRED ${Qt_FIND_REQUIRED})
  SET(Qt4_FIND_QUIETLY  ${Qt_FIND_QUIETLY})
  SET(QT_MIN_VERSION    ${QT4_MIN_VERSION})
  SET(QT_MAX_VERSION    ${QT4_MAX_VERSION})
  INCLUDE(FindQt4)
ENDIF()
IF(DESIRED_QT_VERSION MATCHES 5)
  SET(Qt5_FIND_REQUIRED ${Qt_FIND_REQUIRED})
  SET(Qt5_FIND_QUIETLY  ${Qt_FIND_QUIETLY})
  SET(QT_MIN_VERSION    ${QT5_MIN_VERSION})
  SET(QT_MAX_VERSION    ${QT5_MAX_VERSION})
  INCLUDE(FindQt5)
ENDIF()

IF(NOT QT4_INSTALLED AND NOT QT5_INSTALLED)
  IF(Qt_FIND_REQUIRED)
    MESSAGE(SEND_ERROR "CMake was unable to find any Qt versions, put qmake in your path, or set QTDIR/QT_QMAKE_EXECUTABLE.")
  ENDIF()
ELSE()
  IF(NOT QT_FOUND)
    IF(Qt_FIND_REQUIRED)
      MESSAGE(FATAL_ERROR "CMake was unable to find Qt version: ${DESIRED_QT_VERSION}, put qmake in your path or set QTDIR/QT_QMAKE_EXECUTABLE.")
    ELSE()
      MESSAGE("CMake was unable to find Qt version: ${DESIRED_QT_VERSION}, put qmake in your path or set QTDIR/QT_QMAKE_EXECUTABLE.")
    ENDIF()
  ENDIF()
ENDIF()

MACRO(QT_GET_MOC_FLAGS moc_flags)
  IF(QT_VERSION_MAJOR MATCHES 4)
    QT4_GET_MOC_FLAGS(${moc_flags})
  ELSE()
    IF(QT_VERSION_MAJOR MATCHES 5)
      QT5_GET_MOC_FLAGS(${moc_flags})
    ENDIF()
  ENDIF()
ENDMACRO()

MACRO(QT_CREATE_MOC_COMMAND infile outfile moc_flags moc_options)
  IF(QT_VERSION_MAJOR MATCHES 4)
    IF(CMAKE_VERSION VERSION_GREATER 2.8.11.20130607)
      QT4_CREATE_MOC_COMMAND(${infile} ${outfile} "${moc_flags}" "${moc_options}" "")
    ELSE()
      QT4_CREATE_MOC_COMMAND(${infile} ${outfile} "${moc_flags}" "${moc_options}")
    ENDIF()
  ELSE()
    IF(QT_VERSION_MAJOR MATCHES 5)
      IF(QTVERSION VERSION_GREATER 5.1.99)
        QT5_CREATE_MOC_COMMAND(${infile} ${outfile} "${moc_flags}" "${moc_options}" "")
      ELSE()
        QT5_CREATE_MOC_COMMAND(${infile} ${outfile} "${moc_flags}" "${moc_options}")
      ENDIF()
    ENDIF()
  ENDIF()
ENDMACRO()

MARK_AS_ADVANCED(QT_QMAKE_EXECUTABLE_FINDQT)
