// PriorityQueue.java, created Tue Jun  1 13:43:17 1999 by pnkfelix
// Copyright (C) 1999 Felix S Klock <pnkfelix@mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Util;

import java.util.Collection;

/**
 * <code>MaxPriorityQueue</code> maintains a <code>Collection</code> of
 * <code>Object</code>s, each with an associated priority.
 * Implementations should make the <code>peekMax</code> and
 * <code>removeMax</code> operations efficient.  Implementations
 * need not implement the Object-addition operations of the
 * <code>Collection</code> interface, since they do not associate each
 * added <code>Object</code> with a priority.
 * 
 * @author  Felix S Klock <pnkfelix@mit.edu>
 * @version $Id: MaxPriorityQueue.java,v 1.1.2.1 1999-06-03 01:49:32 pnkfelix Exp $
 */
public interface MaxPriorityQueue extends Collection {
    
    void insert(Object item, int priority);

    Object peekMax();
    
    Object deleteMax();
    
}
