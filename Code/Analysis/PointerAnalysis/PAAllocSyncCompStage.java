// PAAllocSyncCompStage.java, created Fri Apr 18 22:13:12 2003 by salcianu
// Copyright (C) 2003 Alexandru Salcianu <salcianu@MIT.EDU>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Analysis.PointerAnalysis;

import harpoon.ClassFile.HMethod;

import harpoon.Analysis.PointerAnalysis.MAInfo;
import harpoon.Analysis.PointerAnalysis.MAInfo.MAInfoOptions;

import harpoon.Analysis.MetaMethods.MetaCallGraph;
import harpoon.Analysis.MetaMethods.MetaMethod;

import harpoon.Main.CompilerState;
import harpoon.Main.CompilerStage;
import harpoon.Main.CompilerStageEZ;
import harpoon.Main.CompStagePipeline;
import harpoon.Util.Options.Option;

import java.util.List;
import java.util.LinkedList;
import java.util.Set;
import java.util.Iterator;


/**
 * <code>PAAllocSyncCompStage</code>
 * 
 * @author  Alexandru Salcianu <salcianu@MIT.EDU>
 * @version $Id: PAAllocSyncCompStage.java,v 1.1 2003-04-22 00:08:35 salcianu Exp $
 */
public class PAAllocSyncCompStage extends CompStagePipeline {
    
    // TOSOLVE: CURRENTLY, the first stage of the pipeline (pa) is
    // executed even if it is unnecessary (no stack allocation option)

    /** Creates a <code>PAAllocSyncCompStage</code>. */
    public PAAllocSyncCompStage() {
        super(new PointerAnalysisCompStage(true),
	      new OptStage(),
	      "pa-alloc-sync-opt");
    }
    

    public boolean enabled() {
	OptStage optStage = (OptStage) getStage(1);
	// The full pipeline is enabled if the optimization stage (the
	// second and last one) is enabled; otherwise, the pointer
	// analysis object is not constructed (and the required
	// pre-analysis is not executed)
	return optStage.enabled();
    }


    private static class OptStage extends CompilerStageEZ {
	public OptStage() { super("alloc-sync-opt"); }

	private MAInfoOptions maio = new MAInfoOptions();
	private boolean SHOW_ALLOC_PROPERTIES = false;
	
	public List/*<Option>*/ getOptions() {
	    List/*<Option>*/ opts = new LinkedList/*<Option>*/();

	    opts.add(new Option("stack-alloc", "<policy>", "<inlining-depth>",
				"Stack allocation policy: 1 (not in loops) | 2 (whenever is possible); the optional argument <inlining-depth> specifies the maximul level of inlining for improving the stack allocation opportunities (no inlining by default)") {
		public void action() {
		    int policy = Integer.parseInt(getArg(0));
		    switch(policy) {
		    case MAInfoOptions.STACK_ALLOCATE_NOT_IN_LOOPS:
		    case MAInfoOptions.STACK_ALLOCATE_ALWAYS:
			maio.DO_STACK_ALLOCATION = true;
			maio.STACK_ALLOCATION_POLICY = policy;
			// see if any inlining depth is specified
			if(getOptionalArg(0) != null) {
			    int depth = Integer.parseInt(getOptionalArg(0));
			    assert depth >= 0 : 
				"Invalid inlining depth " + depth;
			    maio.MAX_INLINING_LEVEL = depth;
			}
			break;
		    default:
			System.err.println("Unknown stack allocation policy " +
					   policy);
			System.exit(1);
		    }
		}
	    });

	    opts.add(new Option("thread-alloc", "", "prealloc",
				"Thread allocation; CRAZY FEATURE: if the optional argument \"prealloc\" is present, preallocate thread parameters in thread local heap.") {
		public void action() { 
		    maio.DO_THREAD_ALLOCATION = true;
		    if(getOptionalArg(0) != null) {
			assert getOptionalArg(0).equals("prealloc") :
			    "Unknown optional argument for thread-alloc" +
			    getOptionalArg(0);
			maio.DO_PREALLOCATION = true;
		    }
		}
	    });

	    opts.add(new Option("sync-removal", "", "wit",
				"Synchronization removal optimization; if optional argument \"wit\" is present, use the inter-thread pointer analysis.") {
		public void action() {
		    maio.GEN_SYNC_FLAG = true;
		    if(getOptionalArg(0) != null) {
			assert getOptionalArg(0).equals("wit") :
			    "Unknown optional arg for sync-removal" +
			    getOptionalArg(0);
			maio.USE_INTER_THREAD = true;
		    }
		}
	    });

	    opts.add(new Option("show-mainfo", "Show alocation policies") {
		public void action() { SHOW_ALLOC_PROPERTIES = true; }
	    });

	    return opts;
	}


	public boolean enabled() {
	    return
		maio.DO_STACK_ALLOCATION ||
		maio.DO_THREAD_ALLOCATION ||
		maio.GEN_SYNC_FLAG;
	}

	protected void real_action() {
	    PointerAnalysis pa = 
		(PointerAnalysis) attribs.get("PointerAnalysis");

	    MetaCallGraph mcg = pa.getMetaCallGraph();
	    Set allmms = mcg.getAllMetaMethods();
	    
	    // The following loop has just the purpose of timing the
	    // analysis of the entire program. Doing it here, before
	    // any memory allocation optimization, allows us to time
	    // it accurately.
	    long g_tstart = time();
	    for(Iterator it = allmms.iterator(); it.hasNext(); ) {
		MetaMethod mm = (MetaMethod) it.next();
		if(!analyzable(mm)) continue;
		pa.getIntParIntGraph(mm);
	    }
	    System.out.println("Intrathread Analysis time: " +
			       (time() - g_tstart) + "ms");
	    System.out.println("===================================\n");

	    if (maio.USE_INTER_THREAD) {
		g_tstart = System.currentTimeMillis();
		for(Iterator it = allmms.iterator(); it.hasNext(); ) {
		    MetaMethod mm = (MetaMethod) it.next();
		    if(!analyzable(mm)) continue;
		    pa.getIntThreadInteraction(mm);
		}
		System.out.println("Interthread Analysis time: " +
				   (time() - g_tstart) + "ms");
		System.out.println("===================================\n");
	    }
	    
	    g_tstart = time();
	    MAInfo mainfo = new MAInfo(pa, hcf, linker, allmms, maio);
	    System.out.println("GENERATION OF MA INFO TIME  : " +
			       (time() - g_tstart) + "ms");
	    System.out.println("===================================\n");
	    
	    if(SHOW_ALLOC_PROPERTIES) // show allocation policies
		mainfo.print();
	}
    }

    // TODO: change this to invoke hcf.convert and check result against null
    private static boolean analyzable(MetaMethod mm) {
	HMethod hm = mm.getHMethod();
	if(java.lang.reflect.Modifier.isNative(hm.getModifiers()))
	    return false;
	if(java.lang.reflect.Modifier.isAbstract(hm.getModifiers()))
	    return false;
	return true;
    }


    private static long time() {
	return System.currentTimeMillis();
    }
    
}
