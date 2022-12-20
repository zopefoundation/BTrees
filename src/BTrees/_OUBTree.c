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

/* OUBTree - object key, uint32_t value BTree

   Implements a collection using object type keys
   and int type values
*/

#define PERSISTENT

#define MOD_NAME_PREFIX "OU"




#define ZODB_UNSIGNED_VALUE_INTS

#include "_compat.h"
#include "objectkeymacros.h"
#include "intvaluemacros.h"

#define INITMODULE PyInit__OUBTree
#include "BTreeModuleTemplate.c"
