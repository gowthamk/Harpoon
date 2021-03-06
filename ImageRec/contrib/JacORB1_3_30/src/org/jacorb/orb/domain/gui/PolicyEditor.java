package org.jacorb.orb.domain.gui;

/**
 * An  interface for  policy  editors.  Any  class implementing  this
 * interface  is required to manage  a policy of a  certain type. That
 * means a policy editor is bound to a specific type. This type can be
 * retrieved via the operation "getPolicyTypeResponsibleFor".
 *
 * @author Herbert Kiefer
 * @version $Id: PolicyEditor.java,v 1.1 2003-04-03 16:53:19 wbeebee Exp $ 
*/

public interface PolicyEditor
{
    /** 
     *  sets the  policy the  editor  should edit.  reinits the  editor.
     * Because policy editors are  intended be be dynamicly loaded, they
     *  are create  via the  default  constructor. For  that reason  the
     *  policy editor  needs an  initialization.  This is  done by  this
     * operation. 
     */

    public void setEditorPolicy(org.omg.CORBA.Policy policyToEdit);
 
    /** 
     * @return the policy the editor edits.
     */

    public org.omg.CORBA.Policy getEditorPolicy();


    /**
     *  sets the ORB instance shared by the editor and its environment.
     */

    public void setORB(org.omg.CORBA.ORB orb);


    /**
     * @return the policy type this editor is intended for. 
     */

    public int getPolicyTypeResponsibleFor();

    /** 
     * @return the  graphical component  of the  editor.  The graphical
     * component  is used  to display the  editor. Normally this  is the
     * main panel the editor is using.  
     */

    public java.awt.Component getGraphicalComponent();

    /** 
     * returns the title of this editor. The title is a string which is used
     * in grapical displayment to describe the editor. 
     */

    public String getTitle();
  
} // PolicyEditor




