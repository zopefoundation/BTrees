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

#define MASTER_ID "$Id: _OIBTree.c 25186 2004-06-02 15:07:33Z jim $\n"

/* OQBTree - object key, uint64_t value BTree

   Implements a collection using object type keys
   and int type values
*/

#define PERSISTENT

#define MOD_NAME_PREFIX "OQ"




#define ZODB_64BIT_INTS
#define ZODB_UNSIGNED_VALUE_INTS

#include "_compat.h"
#include "objectkeymacros.h"
#include "intvaluemacros.h"

#define INITMODULE PyInit__OQBTree
#include "BTreeModuleTemplate.c"
