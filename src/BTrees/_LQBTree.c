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

#define MASTER_ID "$Id: _IIBTree.c 25186 2004-06-02 15:07:33Z jim $\n"

/* IIBTree - int64_t key, uint64_t value BTree

   Implements a collection using int type keys
   and int type values
*/

/* Setup template macros */

#define PERSISTENT

#define MOD_NAME_PREFIX "LQ"




#define ZODB_64BIT_INTS
#define ZODB_UNSIGNED_VALUE_INTS

#include "_compat.h"
#include "intkeymacros.h"
#include "intvaluemacros.h"

#define INITMODULE PyInit__LQBTree
#include "BTreeModuleTemplate.c"
