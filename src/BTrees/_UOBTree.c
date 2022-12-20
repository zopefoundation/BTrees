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

/* UOBTree - unsigned int key, object value BTree

   Implements a collection using unsigned int type keys
   and object type values
*/

#define PERSISTENT

#define MOD_NAME_PREFIX "UO"



#define ZODB_UNSIGNED_KEY_INTS
#include "_compat.h"
#include "intkeymacros.h"
#include "objectvaluemacros.h"

#define INITMODULE PyInit__UOBTree
#include "BTreeModuleTemplate.c"
