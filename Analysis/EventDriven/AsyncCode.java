// AsyncCode.java, created Thu Nov 11 15:17:54 1999 by kkz
// Copyright (C) 1999 Karen K. Zee <kkzee@alum.mit.edu>
// 		      and Brian Demsky <bdemsky@mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Analysis.EventDriven;

import harpoon.Analysis.ContBuilder.ContBuilder;
import harpoon.Analysis.EnvBuilder.EnvBuilder;
import harpoon.Analysis.Quads.QuadLiveness;
import harpoon.Analysis.ClassHierarchy;
import harpoon.Analysis.Quads.Unreachable;
import harpoon.Analysis.Maps.TypeMap;
import harpoon.ClassFile.CachingCodeFactory;
import harpoon.ClassFile.HClass;
import harpoon.ClassFile.HClassMutator;
import harpoon.ClassFile.HMethod;
import harpoon.ClassFile.HMethodMutator;
import harpoon.ClassFile.HCode;
import harpoon.ClassFile.HConstructor;
import harpoon.ClassFile.HField;
import harpoon.ClassFile.Loader;
import harpoon.ClassFile.Linker;
import harpoon.ClassFile.Relinker;
import harpoon.ClassFile.UniqueName;

import harpoon.IR.Quads.CALL;
import harpoon.IR.Quads.CJMP;
import harpoon.IR.Quads.CONST;
import harpoon.IR.Quads.Code;
import harpoon.IR.Quads.Edge;
import harpoon.IR.Quads.FOOTER;
import harpoon.IR.Quads.GET;
import harpoon.IR.Quads.SET;
import harpoon.IR.Quads.HEADER;
import harpoon.IR.Quads.METHOD;
import harpoon.IR.Quads.NEW;
import harpoon.IR.Quads.OPER;
import harpoon.IR.Quads.Qop;
import harpoon.IR.Quads.PHI;
import harpoon.IR.Quads.Quad;
import harpoon.IR.Quads.QuadFactory;
import harpoon.IR.Quads.QuadNoSSA;
import harpoon.IR.Quads.RETURN;
import harpoon.IR.Quads.THROW;
import harpoon.IR.Quads.TYPECAST;
import harpoon.IR.Quads.QuadVisitor;
import harpoon.Temp.Temp;
import harpoon.Temp.TempFactory;
import harpoon.Temp.CloningTempMap;
import harpoon.Util.Util;
import harpoon.Util.WorkSet;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.lang.reflect.Modifier;

/**
 * <code>AsyncCode</code>
 * 
 * @author Karen K. Zee <kkzee@alum.mit.edu>
 * @version $Id: AsyncCode.java,v 1.1.2.50 2000-02-07 20:36:35 bdemsky Exp $
 */
public class AsyncCode {

    /** Creates a <code>AsyncCode</code>. 
     *
     *  @param hc
     *         the <code>HCode</code> from which to build this
     *         <code>AsyncCode</code>.
     *  @param old2new
     *         the <code>Map</code> mapping blocking methods to the
     *         new Asynchronous version
     *  @param async_todo
     *         the <code>Set</code> of old HCodes for methods to build HCodes 
     *         for the asynchronous versions
     *  @param liveness
     *         results of liveness analysis
     *  @param blockingcalls
     *         set of methods that block
     *  @param ucf
     *         <code>CachingCodeFactory</code> with which to register new
     *         <code>HCode</code>
     *  @param bm
     *         <code>ToAsync.BlockingMethods</code> object which tells
     *         the analysis information about lowest level blocking calls
     */

    public static void buildCode(HCode hc, Map old2new, Set async_todo, 
			   QuadLiveness liveness,
			   Set blockingcalls, 
			   CachingCodeFactory ucf, ToAsync.BlockingMethods bm,
			   HMethod mroot, Linker linker, ClassHierarchy ch,
			   Set other, Set done_other, boolean methodstatus) 
	throws NoClassDefFoundError
    {
	System.out.println("Entering AsyncCode.buildCode()");

	Quad root = (Quad)hc.getRootElement();

	//Cont_todo is the set of quads we need to build continuations for

	WorkSet cont_todo=new WorkSet();
	cont_todo.add(root);

	//contmap maps blocking calls->continuations
	//envmap maps blocking calls->environment class
	HashMap cont_map=new HashMap();
	HashMap env_map=new HashMap();
	
	//iterate through all of the necessary continuations for this HMethod
	while(!cont_todo.isEmpty()) {
	    Quad quadc=(Quad) cont_todo.pop();
	    System.out.println("AsyncCode building continuation for "+quadc);
	    ContVisitor cv=new ContVisitor(cont_todo, async_todo, 
					   old2new, cont_map, 
					   env_map, liveness,
					   blockingcalls, hc.getMethod(), 
					   hc, ucf,bm,mroot, linker,ch,
					   other, done_other,methodstatus);
	    quadc.accept(cv);
	}
    }

    static class ContVisitor extends QuadVisitor {
	WorkSet cont_todo;
	Map old2new, cont_map, env_map;
	Set blockingcalls, async_todo;
	HMethod hmethod;
	boolean header;
	CloningVisitor clonevisit;
	QuadLiveness liveness;
	CachingCodeFactory ucf;
	Linker linker;
	boolean methodstatus;

	public ContVisitor(WorkSet cont_todo, Set async_todo, 
			   Map old2new, Map cont_map, 
			   Map env_map, QuadLiveness liveness,
			   Set blockingcalls, HMethod hmethod, 
			   HCode hc, CachingCodeFactory ucf,
			   ToAsync.BlockingMethods bm, HMethod mroot, 
			   Linker linker, ClassHierarchy ch,
			   Set other, Set done_other, boolean methodstatus) {
	    this.liveness=liveness;
	    this.env_map=env_map;
	    this.cont_todo=cont_todo;
	    this.async_todo=async_todo;
	    this.old2new=old2new;
	    this.cont_map=cont_map;
	    this.blockingcalls=blockingcalls;
	    this.hmethod=hmethod;
	    this.header=false;
	    this.ucf=ucf;
	    this.linker=linker;
	    this.methodstatus=methodstatus;
	    this.clonevisit=new CloningVisitor(blockingcalls, cont_todo,
					       cont_map, env_map, liveness,
					       async_todo, old2new,
					       hc,ucf,bm,mroot, linker,ch,
					       other, done_other,methodstatus);
	}

	public void visit(Quad q) {
	    System.out.println("ERROR: "+q+" in ContVisitory!!!");
	}

	public void visit(HEADER q) {
	    //Handles building HCode's for the HEADER quad...
	    //need to build continuation for this Header...
	    //nmh is the HMethod we wish to attach this HCode to
	    HMethod nhm=methodstatus?hmethod:(HMethod)old2new.get(hmethod);
	    //mark header flag
	    System.out.println("ContVisiting"+ q);
	    header=true;
	    clonevisit.reset(nhm,q.getFactory().tempFactory(),false);
	    System.out.println("Reset clone visitor");
	    copy(q,-1);
	    System.out.println("Finished copying");
	    ucf.put(nhm, clonevisit.getCode());
	}

	public void visit(CALL q) {
	    //builds continuation for CALLs
	    //nmh is the HMethod we wish to attach this HCode to
	    System.out.println("ContVisiting"+ q);
	    HClass hclass=(HClass) cont_map.get(q);
	    HClass throwable=linker.forName("java.lang.Throwable");
	    HMethod resume=(q.method().getReturnType()==HClass.Void)?
		hclass.getDeclaredMethod("resume",new HClass[0])
		:hclass.getDeclaredMethod("resume",
					 new HClass[] {q.method().getReturnType().isPrimitive()?q.method().getReturnType():linker.forName("java.lang.Object")});
	    HMethod exception=
		hclass.getDeclaredMethod("exception",
					 new HClass[] {throwable});

	    //Resume method
	    //have to reset state in visitor class
	    clonevisit.reset(resume,q.getFactory().tempFactory(), true);
	    copy(q,0);
	    System.out.println("Finished resume copying");
	    //addEdges should add appropriate headers
	    ucf.put(resume, clonevisit.getCode());
	    //Exception method
	    clonevisit.reset(exception, q.getFactory().tempFactory(), true);
	    copy(q,1);
	    System.out.println("Finished exception copying");
	    //addEdges should add appropriate headers
	    ucf.put(exception, clonevisit.getCode());
	}

	//copies the necessary quads from the original HCode
	public void copy(Quad q, int resumeexception) {
	    //-1 normal
	    //0 resume
	    //1 exception
	    WorkSet todo=new WorkSet();
	    WorkSet done=new WorkSet();
	    WorkSet dontfollow=new WorkSet();

	    if (resumeexception==-1) {
		//Don't want to visit the footer
		done.add(q.next(0));
		todo.push(q);
	    }
	    else
		todo.push(q.next(resumeexception));
	    while (!todo.isEmpty()) {
		Quad nq=(Quad) todo.pop();
		done.add(nq);
		nq.accept(clonevisit);
		if (clonevisit.follow()) {
		    Quad[] next=nq.next();
		    for (int i=0; i<next.length;i++)
			if (!done.contains(next[i]))
			    todo.push(next[i]);
		} else
		    dontfollow.add(nq);
	    }
	    System.out.println("Start addEdges");
	    clonevisit.addEdges(q,resumeexception,dontfollow);
	    System.out.println("Finished addEdges");
	}

	public boolean isHeader() {
	    return header;
	}
    }

    static class CloningVisitor extends QuadVisitor {
	boolean isCont, followchildren, methodstatus;
	CachingCodeFactory ucf;
	ClassHierarchy ch;
	CloningTempMap ctmap;
	ContCode hcode;
	HashMap quadmap;
	HCode hc;
	HMethod mroot;
	Linker linker;
	Map cont_map, old2new, env_map;	
	Set blockingcalls, cont_todo, async_todo, phiset;
	Set addedCall, other, done_other;
	Temp tthis;
	ToAsync.BlockingMethods bm;
	QuadLiveness liveness;
	WorkSet linkFooters;
	
	public CloningVisitor(Set blockingcalls, Set cont_todo,
			      Map cont_map, Map env_map, 
			      QuadLiveness liveness, Set async_todo,
			      Map old2new, 
			      HCode hc, CachingCodeFactory ucf,
			      ToAsync.BlockingMethods bm, HMethod mroot, 
			      Linker linker, ClassHierarchy ch,
			      Set other, Set done_other, 
			      boolean methodstatus) {
	    this.liveness=liveness;
	    this.blockingcalls=blockingcalls;
	    this.cont_todo=cont_todo;
	    this.cont_map=cont_map;
	    this.async_todo=async_todo;
	    this.old2new=old2new;
	    this.env_map=env_map;
	    this.ucf=ucf;
	    this.hc=hc;
	    this.bm=bm;
	    this.mroot=mroot;
	    this.linker=linker;
	    this.ch=ch;
	    this.other=other;
	    this.done_other=done_other;
	    this.methodstatus=methodstatus;
	}

	public void reset(HMethod nhm, TempFactory otf, boolean isCont) {
	    followchildren=true;
	    hcode=new ContCode(nhm);
	    ctmap=new CloningTempMap(otf,hcode.getFactory().tempFactory());
	    quadmap=new HashMap();
	    this.isCont=isCont;
	    this.linkFooters=new WorkSet();
	    if (isCont)
		tthis=new Temp(hcode.getFactory().tempFactory());
	    else
		tthis=null;
	    phiset=new WorkSet();
	    addedCall=new WorkSet();
	}

	public HCode getCode() {
	    return hcode;
	}

	public boolean follow() {
	    return followchildren;
	}

	HClass getEnv(Quad q) {
	    if (env_map.containsKey(q))
		return (HClass) env_map.get(q);
	    HClass nhclass=(new EnvBuilder(ucf, hc, 
					  q, liveness.getLiveInandOutArray(q),linker)).makeEnv();
	    env_map.put(q, nhclass);
	    return nhclass;
	}


	//Adds edges between quads and environment loading code
	public void addEdges(Quad q, int resumeexception, Set dontfollow) {
	    QuadFactory qf=hcode.getFactory();
	    FOOTER footer=new FOOTER(qf, q, linkFooters.size()+1);
	    Iterator fiterator=linkFooters.iterator();
	    int count=1;
	    while(fiterator.hasNext())
		Quad.addEdge((Quad)fiterator.next(), 0, footer, count++);
	    if (resumeexception!=-1) {
		//Doing addedges for CALL continuation
		//Need to build headers here....[continuation]
		//Need to load environment object and result codes
		
		addEdges(q.next(resumeexception),dontfollow);
		HEADER header=buildEnvironmentExtracter(q, resumeexception,footer);

		fixphis();
		hcode.quadSet(header);
	    } else {
		//Doing addEdges for HEADER
		Quad.addEdge((Quad)quadmap.get(q),1,
			     (Quad)quadmap.get(q.next(1)),q.nextEdge(1).which_pred());
		addEdges(q.next(1),dontfollow);
		//add in new footer
		Quad.addEdge((Quad) quadmap.get(q),0, footer,0);
		fixphis();
		hcode.quadSet((Quad)quadmap.get(q));
	    }
	}

	public void visit(RETURN q) {
	    if (methodstatus) {
		//We are just doing swaps on this method, so just clone
		Object nq=q.clone(hcode.getFactory(), ctmap);
		quadmap.put(q, nq);
		linkFooters.add(nq);
	    } else if (isCont)
		buildReturnContinuation(q, q.retval(), true);
	    else
		buildDoneContinuation(q, q.retval(),true);
	    followchildren=false;
	}
	
	public void visit(THROW q) {
	    TempFactory tf=hcode.getFactory().tempFactory();
	    if (methodstatus) {
		//We are just doing swaps on this method, so just clone
		Object nq=q.clone(hcode.getFactory(), ctmap);
		quadmap.put(q, nq);
		linkFooters.add(nq);
	    } else if (isCont)
		buildReturnContinuation(q, q.throwable(), false);
	    else
		buildDoneContinuation(q, q.throwable(),false);
	    followchildren=false;
	}

	public void visit(Quad q) {
	    followchildren=true;
	    quadmap.put(q, q.clone(hcode.getFactory(), ctmap));
      	}

	public void visit(PHI q) {
	    followchildren=true;
	    Object qc=q.clone(hcode.getFactory(), ctmap);
	    quadmap.put(q, qc);
	    phiset.add(qc);
      	}

	public void visit(CALL q) {
	    checkdoneothers(q.method());
	    if ((methodstatus==false)&&
		(!q.method().getName().equals("<init>"))&&
		isBlocking(q)) {
		if (!cont_map.containsKey(q)) {
		    //Add this CALL to list of calls to build continuations for
		    cont_todo.add(q);
		    //Build Class for the continuation
		    HClass hclass=createContinuation(hc.getMethod(),  q,
						     ucf, linker); 
		    //Add mapping of call->class
		    cont_map.put(q,hclass);
		    //Schedule blocking method for transformation
		    scheduleMethods(q.method());
		}
		handleBlocking(q);
	    } else
		handleNonBlocking(q);
	}


	private void addEdges(Quad q, Set dontfollow) {
	    WorkSet done=new WorkSet();
	    WorkSet todo=new WorkSet();
	    todo.push(q);
	    while (!todo.isEmpty()) {
		Quad nq=(Quad)todo.pop();
		done.add(nq);
		Quad cnq=(Quad)quadmap.get(nq);
		Quad[] next=nq.next();
		if (addedCall.contains(cnq)) {
		    //Handling call with additional call added to it
		    //0 edge is different...we want to link cnq.next(0) instead of cnqq
		    if (!done.contains(next[0]))
			todo.push(next[0]);
		    Quad cn=(Quad)quadmap.get(next[0]);
		    //add the edge in
		    Quad cnq2=cnq.next(0);
		    Quad.addEdge(cnq2,0,cn,nq.nextEdge(0).which_pred());

		    //1 edge is as normal
		    if (!done.contains(next[1]))
			todo.push(next[1]);
		    cn=(Quad)quadmap.get(next[1]);
		    //add the exception edge in
		    Quad.addEdge(cnq,1,cn,nq.nextEdge(1).which_pred());
		} else if (!dontfollow.contains(nq))
		    for (int i=0;i<next.length;i++) {
			//this quad was cloned
			if (!done.contains(next[i]))
			    todo.push(next[i]);
			Quad cn=(Quad)quadmap.get(next[i]);
			//add the edge in
			Quad.addEdge(cnq,i,cn,nq.nextEdge(i).which_pred());
		    }
	    }
	}

	private HEADER buildEnvironmentExtracter(Quad q, int resumeexception, Quad footer){
	    QuadFactory qf=hcode.getFactory();
	    TempFactory tf=qf.tempFactory();
	    //-----------------------------------------------------------------
	    //Build HEADER
	    
	    Quad first=(Quad) quadmap.get(q.next(resumeexception));
	    Temp oldrtemp=
		(resumeexception == 0) ?
		((CALL)q).retval():((CALL)q).retex();
	    Temp[] params=null;
	    if (oldrtemp==null)
		params=new Temp[1];
	    else {
		params=new Temp[2];
		params[1]=ctmap.tempMap(oldrtemp);
	    }
	    params[0]=tthis;
	    HEADER header=new HEADER(qf,first);
	    
	    //-----------------------------------------------------------------
	    //Build METHOD quad
	    //
	    
	    
	    Quad.addEdge(header,0,footer,0);
	    METHOD method=new METHOD(qf,first,params,1);
	    Quad.addEdge(header,1,method,0);
	    Temp tenv=new Temp(tf);
	    
	    //-----------------------------------------------------------------
	    //Build GET quad for environment
	    //
	    
	    GET get=
		new GET(qf,first,tenv,
			hcode.getMethod().getDeclaringClass().getField("e"),
			method.params(0));
	    Quad.addEdge(method,0,get,0);
	    

	    //-----------------------------------------------------------------
	    //GET Temp's out of environment
	    //
	    // assign each field in the Environment to the appropriate Temp
	    // except for the assignment we want to suppress
	    
	    Temp suppress =
		(resumeexception == 0) ?
		((CALL)q).retval() : ((CALL)q).retex();
	    Temp[] liveout=liveness.getLiveInandOutArray(q);

	    Quad prev = get;
	    HField[] envfields=getEnv(q).getDeclaredFields();
	    TypeMap map=((QuadNoSSA) this.hc).typeMap;
	    
	    //Build string of CONST's and GET's.
	    
	    for(int i=0,j=0; i<liveout.length; i++) {
		if (suppress == null || !suppress.equals(liveout[i])) {
		    Quad ng =(map.typeMap(q, liveout[i])!=HClass.Void)? 
			((Quad)new GET(qf, first, ctmap.tempMap(liveout[i]),
				       envfields[j], tenv)):
			((Quad)new CONST(qf, first, ctmap.tempMap(liveout[i]),
					 null, HClass.Void));
		    Quad.addEdge(prev, 0, ng, 0);
		    prev = ng;
		}
		if (map.typeMap(q,liveout[i])!=HClass.Void)
		    j++;
	    }
	    //-----------------------------------------------------------------
	    // Typecast the argument to resume if necessary
	    if (!((CALL)q).method().getReturnType().isPrimitive()) {
		TYPECAST tc = 
		    new TYPECAST(qf, first, 
				 ((CALL)q).retval(),
				 ((CALL)q).method().getReturnType());
		Quad.addEdge(prev, 0, tc, 0);
		prev = tc;
	    }
	    //-----------------------------------------------------------------
	    //Link in header code to body of method
	    Quad.addEdge(prev,0,
			 (Quad)quadmap.get(q.next(resumeexception)),
			 q.nextEdge(resumeexception).which_pred());
	    return header;
	}
	

	/**Shrinks PHI's as needed.*/

	private void fixphis() {
	    Iterator phiit=phiset.iterator();
	    while(phiit.hasNext()) {
		PHI phi=(PHI) phiit.next();
		for (int i=phi.arity()-1;i>=0;i--)
		    if (phi.prevEdge(i)==null) {
			phi=phi.shrink(i);
		    }
	    }
	}
	
	/**On some methods, we need to check to see if we are top level
	 *so that we return instead of resume.*/

	private boolean needsCheck() {
	    HMethod m=hc.getMethod();
	    HClass hcl=m.getDeclaringClass();

	    if (linker.forName("java.lang.Runnable").
		isSuperinterfaceOf(hcl)&&
		hcl.getMethod("run",new HClass[0]).equals(m))
		return true;
	    if (m.equals(mroot))
		return true;
	    return false;
	}

	private void buildReturnContinuation(Quad q, Temp retthrowtemp, boolean isReturn) {
	    TempFactory tf=hcode.getFactory().tempFactory();
	    //----------------------------------------------------------------------------
	    //build GET next Quad
	    HClass hclass=hcode.getMethod().getDeclaringClass();
	    HField hfield=hclass.getField("next");
	    Temp tnext=new Temp(tf);
	    GET get=new GET(hcode.getFactory(),q,
			    tnext, hfield, tthis);
	    
	    //----------------------------------------------------------------------------
	    //We may need to add null check on next field
	    //If null (ie run_Async, main method), we need to return instead
	    //of calling resume
	    
	    Quad nq=get;
	    if (needsCheck()) {
		Temp tnull=new Temp(tf);
		CONST qconst=
		    new CONST(hcode.getFactory(), q, tnull, null, HClass.Void);
		Quad.addEdge(nq,0,qconst,0);
		Temp tcomp=new Temp(tf);
		OPER qoper=
		    new OPER(hcode.getFactory(),q,Qop.ACMPEQ,tcomp, 
			     new Temp[] {tnext, tnull});
		Quad.addEdge(qconst, 0, qoper, 0);
		CJMP cjmp=
		    new CJMP(hcode.getFactory(), q, tcomp, new Temp[0]);
		Quad.addEdge(qoper, 0, cjmp, 0);
		nq=cjmp;
	    }
	    //----------------------------------------------------------------------------
	    //Build the call to resume
	    
	    Temp retex=new Temp(tf);
	    CALL call=null;
	    if (!isReturn) {
		HClass throwable=linker.forName("java.lang.Throwable");
		HMethod resume=hfield.getType().getMethod("exception",
							  new HClass[] {throwable});
		Temp nretval=ctmap.tempMap(retthrowtemp);
		call=new CALL(hcode.getFactory(), q, resume,
			      new Temp[] {tnext,nretval},null,retex,
			      true,false,new Temp[0]);
	    } else if (hc.getMethod().getReturnType()!=HClass.Void) {
		HMethod resume=(hc.getMethod().getReturnType().isPrimitive())?
		    hfield.getType().getMethod("resume",
					       new HClass[] {hc.getMethod().getReturnType()}):
		    hfield.getType().getMethod("resume",
					       new HClass[] {linker.forName("java.lang.Object")});
		    
		Temp nretval=ctmap.tempMap(retthrowtemp);
		//***** Tailcall eventually
		call=new CALL(hcode.getFactory(), q, resume,
			      new Temp[] {tnext,nretval},null,retex,
			      true,false,new Temp[0]);
	    } else {
		HMethod resume=hfield.getType().getMethod("resume", new HClass[0]);
		//***** Tailcall eventually
		call=new CALL(hcode.getFactory(), q, resume,
			      new Temp[] {tnext}, null, retex,
			      true, false, new Temp[0]);
	    }
	    
	    //---------------------------------------------------------------------------
	    //Build THROW and RETURN quads
	    
	    Quad.addEdge(nq,0,call,0);
	    THROW qthrow=new THROW(hcode.getFactory(),q,retex);
	    RETURN qreturn=new RETURN(hcode.getFactory(),q,null);
	    if (isReturn)
		Quad.addEdge(call,1,qthrow,0);
	    else
		Quad.addEdge(call,0, qreturn,0);
	    linkFooters.add(qthrow);
	    linkFooters.add(qreturn);
	    
	    //---------------------------------------------------------------------------
	    //If top level [main or run] link in possible RETURN edges
	    //otherwise just link in 0 edge of the call to resume
	    
	    if (needsCheck()) {
		PHI phi=new PHI(hcode.getFactory(), q, new Temp[0], 2);
		Quad.addEdge(nq, 1, phi, 0);
		if (isReturn) {
		    Quad.addEdge(call,0,phi,1);
		    Quad.addEdge(phi,0,qreturn,0);
		} else {
		    Quad.addEdge(call,1,phi,1);
		    Quad.addEdge(phi,0,qthrow,0);
		}
	    } else
		if (isReturn)
		    Quad.addEdge(call,0,qreturn,0);
		else
		    Quad.addEdge(call,1,qthrow,0);
	    quadmap.put(q, get);
	}

	private void buildDoneContinuation(Quad q, Temp retthrowtemp, boolean isReturn) {
	    TempFactory tf=hcode.getFactory().tempFactory();
	    //--------------------------------------------------------------------------
	    //Build NEW temp for DoneContinuation
	    
	    HClass rettype=hc.getMethod().getReturnType();
	    String pref = 
		ContBuilder.getPrefix(rettype);
	    HClass continuation = linker.forName
		("harpoon.Analysis.ContBuilder." + pref + "DoneContinuation");
	    Temp newt=new Temp(tf);
	    NEW newq=new NEW(hcode.getFactory(),q,newt, continuation);
	    

	    //---------------------------------------------------------------------------
	    //Build CALL to DoneContinuation constructor

	    Temp retex=new Temp(tf);
	    HClass ret=isReturn?
		(rettype.isPrimitive()?rettype:linker.forName("java.lang.Object"))
		:linker.forName("java.lang.Throwable");
	    HConstructor constructor=(ret!=HClass.Void)?continuation.getConstructor(new HClass[]{ret}):
		continuation.getConstructor(new HClass[0]);
	    CALL call;
	    if (retthrowtemp!=null) {
		//***** Tailcall eventually
		Temp nretval=ctmap.tempMap(retthrowtemp);
		call=new CALL(hcode.getFactory(), q, constructor,
			      new Temp[] {newt,nretval}, null,retex,
			      false,false,new Temp[0]);
	    } else {
		//***** Tailcall eventually
		call=new CALL(hcode.getFactory(), q, constructor,
			      new Temp[] {newt}, null, retex,
			      false, false, new Temp[0]);
	    }

	    //---------------------------------------------------------------------------
	    //Add return and throw quads
	    
	    Quad.addEdge(newq,0,call,0);
	    THROW qthrow=new THROW(hcode.getFactory(),q,retex);
	    
	    Quad.addEdge(call,1,qthrow,0);
	    RETURN qreturn=new RETURN(hcode.getFactory(),q,newt);
	    Quad.addEdge(call,0,qreturn,0);
	    linkFooters.add(qthrow);
	    linkFooters.add(qreturn);
	    quadmap.put(q, newq);
	}


	private boolean isBlocking(CALL q) {
	    HMethod hm=q.method();
	    if (blockingcalls.contains(hm))
		return true;
	    HClass bclass=hm.getDeclaringClass();
	    Set hchilds=ch.children(bclass);
	    Iterator childit=hchilds.iterator();
	    while (childit.hasNext()) {
		try {
		    HClass child=(HClass)childit.next();
		    HMethod hmtest=child.getDeclaredMethod(hm.getName(),
							   hm.getParameterTypes());
		    if (blockingcalls.contains(hmtest))
			return true;
		} catch (NoSuchMethodError e) {
		}
	    }
	    return false;
	}

	private void checkdoneothers(HMethod ohm) {
	    //make sure we actually rewrite all methods that we can reach...
	    if (!done_other.contains(ohm)) {
		HMethod hm=ohm;
		HClass hcl=hm.getDeclaringClass();
		if ((!linker.forName("java.lang.Thread").equals(hcl))||
		    (!hm.getName().equals("run_Async"))) {
		    Set classes=ch.children(hcl);
		    Iterator childit=classes.iterator();
		    HMethod parent=ohm;
		    while (childit.hasNext()|(hm!=null)) {
			try {
			    if (hm==null) {
				HClass child=(HClass)childit.next();
				hm=child.getDeclaredMethod(parent.getName(),
							   parent.getParameterTypes());
				if (done_other.contains(hm)) {
				    hm=null;
				    continue;
				}
			    }
			} catch (NoSuchMethodError e) {
			}
			if (hm!=null) {
			    other.add(hm);
			    hm=null;
			}
		    }
		}
	    }
	}
	
	private void scheduleMethods(HMethod hm) {
	    if (!old2new.containsKey(hm)) {
		HClass hcl=hm.getDeclaringClass();
		Set classes=ch.children(hcl);
		Iterator childit=classes.iterator();
		HMethod parent=hm;
		while (childit.hasNext()|(hm!=null)) {
		    try {
			if (hm==null) {
			    HClass child=(HClass)childit.next();
			    hm=child.getDeclaredMethod(parent.getName(),
						       parent.getParameterTypes());
			    if (old2new.containsKey(hm)) {
				hm=null;
				continue;
			    }
			}
			if (bm.swop(hm)!=null) {
			    //handle actual blocking call swapping
			    old2new.put(hm, bm.swop(hm));
			} else {
			    if (hm.getName().compareTo("<init>")!=0) {
				HCode toConvert=ucf.convert(hm);
				if (toConvert!=null)
				    async_todo.add(toConvert);
				else if (Modifier.isNative(hm.getModifiers()))
				    System.out.println("XXX:ERROR Native blocking: "+hm);
				HMethod temp=makeAsync(old2new, hm,
						       ucf,linker);
			    } else {
				System.out.println("XXX:ERROR "+hm+" is blocking!");
			    }
			}
		    } catch (NoSuchMethodError e) {
		    }
		    hm=null;
		}
	    }
	}

	private void handleBlocking(CALL q) {
	    TempFactory tf=hcode.getFactory().tempFactory();

	    //--------------------------------------------------------------------
	    //Rewrite the Blocking Call
	    
	    Temp[] newt=new Temp[q.paramsLength()];
	    Temp retex=new Temp(tf), retcont=new Temp(tf);
	    for(int i=0;i<q.paramsLength();i++)
		newt[i]=ctmap.tempMap(q.params(i));
	    HMethod calleemethod=(HMethod)old2new.get(q.method());
	    CALL call=new CALL(hcode.getFactory(),q,
			       calleemethod, newt,
			       retcont,retex, q.isVirtual(), q.isTailCall(),
			       new Temp[0]);
	    
	    //---------------------------------------------------------------------
	    //Build phi node for exception handler
	    PHI phi=new PHI(hcode.getFactory(), q, new Temp[0], isCont?5:4);
	    Quad.addEdge(call,1,phi,0);
	    
	    //---------------------------------------------------------------------
	    //Build array of temps to pass into Enviroment's constructor
	    Temp tenv=new Temp(tf);
	    Temp[] liveoutx = liveness.getLiveInandOutArray(q);
	    TypeMap map=((QuadNoSSA) hc).typeMap;
	    int count=0;
	    for (int ii=0;ii<liveoutx.length;ii++)
		if (map.typeMap(q,liveoutx[ii])!=HClass.Void)
		    count++;
	    Temp [] params = new Temp[count+1];
	    params[0]=tenv;
	    for (int j=0,i=1;j<liveoutx.length;j++) {
		if (map.typeMap(q,liveoutx[j])!=HClass.Void)
		    params[i++]=ctmap.tempMap(liveoutx[j]); 
	    }
	    
	    //---------------------------------------------------------------------
	    //Build Environment NEW & CALL to init
	    HClass env=getEnv(q);
	    NEW envq=new NEW(hcode.getFactory(), q, tenv, env);
	    Quad.addEdge(call,0,envq,0);
	    CALL callenv=new CALL(hcode.getFactory(), q, env.getConstructors()[0],
				  params, null, retex, false, false, new Temp[0]);
	    Quad.addEdge(envq,0,callenv,0);
	    Quad.addEdge(callenv,1,phi,1);
		
	    //---------------------------------------------------------------------
	    //Build Continuation NEW & CALL to init
	    
	    Temp tcont=new Temp(tf);
	    HClass contclass=(HClass)cont_map.get(q);
	    NEW newc=new NEW(hcode.getFactory(), q, tcont, contclass);
	    Quad.addEdge(callenv,0,newc,0);
	    HClass environment=linker.forName("harpoon.Analysis.EnvBuilder.Environment");
	    HConstructor call2const=contclass.getConstructor(new HClass[]{
		environment});
	    CALL call2=new CALL(hcode.getFactory(),q,
				call2const,
				new Temp[] {tcont, tenv}, null, retex, 
				false, false, new Temp[0]);
	    Quad.addEdge(newc,0,call2,0);
	    Quad.addEdge(call2,1,phi,2);
	    
	    //----------------------------------------------------------------------
	    //Link new Continuation onto Continuation returned by blocking call
	    String pref = 
		ContBuilder.getPrefix(q.method().getReturnType());
	    HClass[] nextarray=
		new HClass[] {linker.forName("harpoon.Analysis.ContBuilder."+pref+"ResultContinuation")};
	    HMethod setnextmethod=
		calleemethod.getReturnType().getMethod("setNext",nextarray);
	    Util.assert(setnextmethod!=null,"no setNext method found");
	    CALL call3=new CALL(hcode.getFactory(), q,
				setnextmethod, new Temp[] {retcont, tcont},
				null, retex, true, false, new Temp[0]);
	    Quad.addEdge(call2, 0, call3, 0);
	    Quad.addEdge(call3, 1, phi, 3);


	    //----------------------------------------------------------------------
	    //Two possibilities:
	    //1)  We are a continuation, so we want to do a setNext(this.next)
	    //2)  We are a Async method, so we want to return continuation
	    
	    if (isCont) {
		Temp tnext=new Temp(tf);
		HClass hclass=hcode.getMethod().getDeclaringClass();
		HField hfield=hclass.getField("next");
		GET get=new GET(hcode.getFactory(),q,
				tnext, hfield, tthis);
		Quad.addEdge(call3,0,get,0);
		String pref2 =
		    ContBuilder.getPrefix(hc.getMethod().getReturnType());
		HMethod setnextmethod2=
		    contclass.getMethod("setNext",
					new HClass[] {linker.forName("harpoon.Analysis.ContBuilder."+pref2+"ResultContinuation")});
		Util.assert(setnextmethod2!=null,"no setNext method found");
		CALL call4=new CALL(hcode.getFactory(), q,
				    setnextmethod2, new Temp[] {tcont, tnext},
				    null, retex, true, false, new Temp[0]);
		Quad.addEdge(get,0,call4,0);
		Quad.addEdge(call4,1,phi,4);
		RETURN returnq=new RETURN(hcode.getFactory(), q, null);
		Quad.addEdge(call4,0,returnq,0);
		linkFooters.add(returnq);
	    } else {
		RETURN returnq=new RETURN(hcode.getFactory(),q,tcont);
		Quad.addEdge(call3, 0, returnq,0);
		linkFooters.add(returnq);
	    }
	    //---------------------------------------------------------------
	    //Do THROW of exceptions from phi node
	    
	    THROW throwq=new THROW(hcode.getFactory(),q,retex);    
	    Quad.addEdge(phi,0,throwq,0);
	    linkFooters.add(throwq);
	    quadmap.put(q,call);
	    followchildren=false;
	}

	private void handleNonBlocking(CALL q) {
	    followchildren=true;
	    TempFactory tf=hcode.getFactory().tempFactory();
	    //need to check if swop necessary
	    if (swapTo(q.method())!=null) {
		//need to swop this method for replacement
		Temp tstream=ctmap.tempMap(q.params(0));
		quadmap.put(q,new CALL(hcode.getFactory(), q, swapTo(q.method()),
				       new Temp[]{tstream}, 
				       (q.retval()==null)?null:ctmap.tempMap(q.retval()),
				       (q.retex()==null)?null:ctmap.tempMap(q.retex()), q.isVirtual(),
				       q.isTailCall(), new Temp[0]));
	    } else if (swapAdd(q.method())!=null) {
		//need to add an additional call [for makeAsync's, etc]
		CALL cq=(CALL)q.clone(hcode.getFactory(), ctmap);
		quadmap.put(q, cq);
		Temp retex=new Temp(tf);
		CALL nc=new CALL(hcode.getFactory(), q,
				 swapAdd(q.method()), 
				 new Temp[] {cq.params(0)},
				 null, retex, true, false, new Temp[0]);
		Quad.addEdge(cq,0,nc, 0);
		THROW nt=new THROW(hcode.getFactory(), q,
				   retex);
		Quad.addEdge(nc,1,nt,0);
		addedCall.add(cq);
		linkFooters.add(nt);
	    } else
		quadmap.put(q, q.clone(hcode.getFactory(), ctmap));
	}


	/**
	 * swapAdd takes in an <code>HMethod</code> and returns an <code>HMethod</code>
	 * that is to be called following the first method is called.
	 */
	public HMethod swapAdd(HMethod old) {
	    HClass ss=linker.forName("java.net.ServerSocket");
	    HClass fis=linker.forName("java.io.FileInputStream");
	    if (old.equals(ss.getConstructor(new HClass[] {HClass.Int,
							       HClass.Int,
							       linker.forName("java.net.InetAddress")})))
		return ss.getDeclaredMethod("makeAsync", new HClass[0]);
	    if (old.equals(fis.getConstructor(new HClass[] {linker.forName("java.lang.String")}))||
		old.equals(fis.getConstructor(new HClass[] {linker.forName("java.io.FileDescriptor")})))
		return fis.getDeclaredMethod("makeAsync", new HClass[0]);
	    return null;
	}

	/**
	 * swapTo takes in an <code>HMethod</code> and returns an <code>HMethod</code>
	 * that is to be called following the first method is called.
	 */

	public HMethod swapTo(HMethod old) {
	    //Handle Socket getInputStream calls
	    HMethod gis=linker.forName("java.net.Socket")
		.getDeclaredMethod("getInputStream", new HClass[0]);
	    if (gis.equals(old))
		return linker.forName("java.net.Socket").getDeclaredMethod
		    ("getAsyncInputStream", new HClass[0]);
	    

	    //Handle Socket getOutputStream calls
	    HMethod  gos=linker.forName("java.net.Socket")
		.getDeclaredMethod("getOutputStream", new HClass[0]);
	    if (gos.equals(old))
		return linker.forName("java.net.Socket").getDeclaredMethod
		    ("getAsyncOutputStream", new HClass[0]);
	    

	    //Handle start calls
	    HClass HCthrd=linker.forName("java.lang.Thread");
	    if (old.equals(HCthrd.getMethod("start",
					    new HClass[0]))) {
		HMethod hmrun=old.getDeclaringClass().getMethod("run",
							       new HClass[0]);
		scheduleMethods(hmrun);
		return old.getDeclaringClass().getMethod("start_Async",
							 new HClass[0]);
	    }

	    //No match found
	    return null;
	}
    }

    static class ChangingVisitor extends QuadVisitor {
	HClass oldn, newn;
	WorkSet done;
	ChangingVisitor(HClass oldn, HClass newn) {
	    this.oldn=oldn;
	    this.newn=newn;
	}

	public void visit(Quad q) {
	    done.add(q);
	}

	public void visit(GET q) {
	    if (q.field().getDeclaringClass()==oldn) {
		HField hfield=
		    newn.getDeclaredField(q.field().getName());
		GET get=new GET(q.getFactory(),q,
				q.dst(),hfield,q.objectref());
		done.add(get);
		Quad.addEdge(q.prev(0),q.prevEdge(0).which_succ(),
			     get,0);
		Quad.addEdge(get,0,
			     q.next(0),q.nextEdge(0).which_pred());
	    }
	}

	public void visit(SET q) {
	    if (q.field().getDeclaringClass()==oldn) {
		HField hfield=
		    newn.getDeclaredField(q.field().getName());
		SET set=new SET(q.getFactory(),q,
				hfield,q.objectref(),q.src());
		done.add(set);
		Quad.addEdge(q.prev(0),q.prevEdge(0).which_succ(),
			     set,0);
		Quad.addEdge(set,0,
			     q.next(0),q.nextEdge(0).which_pred());
	    }
	}

	public void reName(Quad q) {
	    done=new WorkSet();
	    WorkSet todo=new WorkSet();
	    todo.add(q);
	    while(!todo.isEmpty()) {
		Quad qq=(Quad)todo.pop();
		Quad[] next=qq.next();
		for(int i=0;i<next.length;i++)
		    if (!done.contains(next[i]))
			todo.add(next[i]);
		qq.accept(this);
	    }
	}
    }



    // create asynchronous version of HMethod to replace blocking version
    // does not create HCode that goes w/ it...
    public static HMethod makeAsync(Map old2new, HMethod original,
			      CachingCodeFactory ucf, Linker linker)
    {
	//	final HMethod original = blocking.method();
	HClass originalClass = original.getDeclaringClass();
	HClassMutator originalMutator=originalClass.getMutator();
	Util.assert(originalMutator!=null);
  
	// use the return type of the original HMethod to get the String 
	// prefix for the type of Continuation we want as the new return type
	final String pref = ContBuilder.getPrefix(original.getReturnType());

	// get the return type for the replacement HMethod
	final HClass newReturnType = linker.forName
	    ("harpoon.Analysis.ContBuilder." + pref + "Continuation");

	// find a unique name for the replacement HMethod
	String methodNamePrefix = original.getName() + "_Async";
	String newMethodName = methodNamePrefix;
	boolean threadrun=false;
	if (linker.forName("java.lang.Runnable").
	    isSuperinterfaceOf(originalClass)&&
	    originalClass.getMethod("run",new HClass[0]).equals(original)) {
	    try {
		newMethodName = methodNamePrefix;
		originalClass.getDeclaredMethod(newMethodName, 
					   original.getParameterTypes());
		if (originalClass.getName().compareTo("java.lang.Thread")!=0)
		    throw new RuntimeException("Name collision with run_Async method");
		else
		    threadrun=true;
	    } catch (NoSuchMethodError e) {
	    }
	} else {
	    try {
		newMethodName = methodNamePrefix + "$$$"; 
		originalClass.getDeclaredMethod(newMethodName, 
					original.getParameterTypes());
		throw new RuntimeException("Name collision with "+newMethodName+ " method");
	    } catch (NoSuchMethodError e) {
	    }
	}
	// create replacement method
	HMethod replacement=null;
	if (!threadrun) {
	    replacement=originalMutator.addDeclaredMethod(newMethodName, 
							  original.getParameterTypes(),
							  newReturnType);
	    HMethodMutator rmutator=replacement.getMutator();
	    rmutator.setExceptionTypes(original.getExceptionTypes());
	    rmutator.setModifiers(original.getModifiers());
	    rmutator.setParameterNames(original.getParameterNames());
	    rmutator.setSynthetic(original.isSynthetic());
	} else {
	    replacement=originalClass.getDeclaredMethod(newMethodName,
							original.getParameterTypes());
	    HMethodMutator rmutator=replacement.getMutator();
	    rmutator.setReturnType(newReturnType);
	}

	old2new.put(original, replacement);
	return replacement;
    }

    // creates the HClass and constructor for the continuation
    private static HClass createContinuation(HMethod blocking, CALL callsite,
				      CachingCodeFactory ucf, Linker linker) 
	throws NoClassDefFoundError
    {
	final HClass template = 
	    linker.forName("harpoon.Analysis.ContBuilder.ContTemplate");

	String cname=UniqueName.uniqueClassName("harpoon.Analysis.ContBuilder.ContTemplate"
						,linker);
	HClass continuationClass = linker.createMutableClass(cname,template);
	Util.assert(template.getLinker()==linker &&
		    continuationClass.getLinker()==linker);
	HClassMutator contMutator=continuationClass.getMutator();
	    //new HClassSyn(template);
	final int numConstructors = continuationClass.getConstructors().length;
	Util.assert(numConstructors == 1,
		    "Found " + numConstructors + " constructors in " +
		    "ContTemplate. Expected one");

	// use the return type of the blocking HMethod to get the String 
	// prefix for the superclass for the continuation we want to create
	final String superPref = 
	    ContBuilder.getPrefix(blocking.getReturnType());

	// get the superclass for the continuation
	final HClass superclass = linker.forName
	    ("harpoon.Analysis.ContBuilder." + superPref + "Continuation");

	contMutator.setSuperclass(superclass);

	// we want the return type of the blocking call
	// this gives us the interface that our continuation should implement
	final String interPref = 
	    ContBuilder.getPrefix(callsite.method().getReturnType());

	// get the interface that the continuation needs to implement
	final HClass inter = linker.forName("harpoon.Analysis.ContBuilder." + 
					    interPref + "ResultContinuation");
	contMutator.addInterface(inter);

	HMethod hmethods[]=template.getDeclaredMethods();
	for(int i=0;i<hmethods.length;i++) {
	    try {
		HMethod nhm=continuationClass
		    .getDeclaredMethod(hmethods[i].getName(),
				       hmethods[i].getDescriptor());
		HCode hchc = ((Code)ucf.convert(hmethods[i])).clone(nhm);
		(new ChangingVisitor(template,continuationClass))
		    .reName((Quad)hchc.getRootElement());
		ucf.put(nhm, hchc);
	    } catch (NoSuchMethodError e) {
		System.err.println(e);
	    }
	}

	HMethod hm = continuationClass.getDeclaredMethod("resume", new HClass[0]);
	HMethodMutator hmMutator=hm.getMutator();

	// get the return value of the blocking call
	// this is the parameter of the resume method, if any
	HClass rettype = callsite.method().getReturnType();
	Temp retval = callsite.retval();
	boolean hasParameter = false;
	if (retval != null) {
	    hasParameter = true;
	    String[] parameterNames = new String[1];
	    parameterNames[0] = retval.name();
	    HClass[] parameterTypes = new HClass[1];
	    if (rettype.isPrimitive())
		parameterTypes[0] = rettype;
	    else {
		parameterTypes[0] = linker.forName("java.lang.Object");
	    }
	    hmMutator.setParameterNames(parameterNames);
	    hmMutator.setParameterTypes(parameterTypes);
	}
	return continuationClass;
    }
}
