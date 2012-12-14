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

/* OIBTree - object key, int value BTree

   Implements a collection using object type keys
   and int type values
*/

#define PERSISTENT

#define MOD_NAME_PREFIX "OI"

#define DEFAULT_MAX_BUCKET_SIZE 60
#define DEFAULT_MAX_BTREE_SIZE 250
                                
#include "_compat.h"
#include "objectkeymacros.h"
#include "intvaluemacros.h"

#ifdef PY3K
#define INITMODULE PyInit__OIBTree
#else
#define INITMODULE init_OIBTree
#endif
#include "BTreeModuleTemplate.c"
