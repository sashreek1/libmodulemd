/*
 * This file is part of libmodulemd
 * Copyright (C) 2017-2018 Stephen Gallagher
 *
 * Fedora-License-Identifier: MIT
 * SPDX-2.0-License-Identifier: MIT
 * SPDX-3.0-License-Identifier: MIT
 *
 * This program is free software.
 * For more information on the license, see COPYING.
 * For more information on free software, see <https://www.gnu.org/philosophy/free-sw.en.html>.
 */

#pragma once

#include <glib.h>

#include "config.h"

/* GDate autoptr cleanup was finally added in GLib 2.63.3. */
#ifndef HAVE_GDATE_AUTOPTR
G_DEFINE_AUTOPTR_CLEANUP_FUNC (GDate, g_date_free)
#endif
