// CleanUp.java, created Sat Sep 12 20:23:54 1998 by cananian
package harpoon.IR.QuadSSA;

import java.util.Hashtable;
import java.util.Enumeration;

import harpoon.ClassFile.*;
import harpoon.Temp.Temp;
import harpoon.Temp.TempMap;
import harpoon.Util.NullEnumerator;
import harpoon.Util.Util;
import harpoon.Util.Set;
import harpoon.Util.Worklist;

/**
 * <code>CleanUp</code> cleans up the phi functions of the IR generated
 * by the <code>Translate</code> class.<p>
 * It: <UL>
 * <LI> Removes phi/sigma functions that define temps that are never used
 *      (which magically removes undefined temps as well).
 * <LI> Shrinks phi functions that have phantom limbs 
 *      (from impossible catches).
 * </UL>
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: CleanUp.java,v 1.9 1998-09-22 02:32:15 cananian Exp $
 * @see Translate
 */

class CleanUp  {
    static void cleanup(Code c) {
	// iterate over all phis.
	for(Enumeration e=c.getElementsE(); e.hasMoreElements(); ) {
	    Quad q = (Quad) e.nextElement();
	    if (! (q instanceof PHI) ) continue;
	    PHI phi = (PHI) q;
	    // shrink phi functions with null limbs.
	    for (int j=0; j<phi.prev.length; )
		if (phi.prev[j]==null)
		    phi.remove(j);
		else j++;
	}
    }
}
