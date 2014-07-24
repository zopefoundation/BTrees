/*############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################*/

#define MASTER_ID "$Id$\n"

/* IBBTree - int key, byte value BTree

   Implements a collection using int type keys
   and byte type values
*/

/* Setup template macros */

#define PERSISTENT

#define MOD_NAME_PREFIX "IB"

#define DEFAULT_MAX_BUCKET_SIZE 120
#define DEFAULT_MAX_BTREE_SIZE 500

#include "_compat.h"
#include "intkeymacros.h"
#include "bytevaluemacros.h"

#ifdef PY3K
#define INITMODULE PyInit__IBBTree
#else
#define INITMODULE init_IBBTree
#endif
#include "BTreeModuleTemplate.c"
