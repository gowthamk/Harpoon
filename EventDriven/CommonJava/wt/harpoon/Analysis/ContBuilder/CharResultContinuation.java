// CharResultContinuation.java, created Fri Nov  5 14:34:24 1999 by kkz
// Copyright (C) 1999 Karen K. Zee <kkzee@alum.mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Analysis.ContBuilder;

/**
 * <code>CharResultContinuation</code>
 * 
 * @author Karen K. Zee <kkzee@alum.mit.edu>
 * @version $Id: CharResultContinuation.java,v 1.1 2000-03-24 02:32:25 govereau Exp $
 */
public interface CharResultContinuation extends Continuation {

    public void resume(char result);

}