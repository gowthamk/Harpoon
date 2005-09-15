// Flags.java, created Wed Jul 20 06:31:03 2005 by salcianu
// Copyright (C) 2003 Alexandru Salcianu <salcianu@alum.mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Analysis.PA2;

import java.util.List;
import java.util.LinkedList;
import java.util.Arrays;

import harpoon.Util.Options.Option;

/**
 * <code>Flags</code>
 * 
 * @author  Alexandru Salcianu <salcianu@alum.mit.edu>
 * @version $Id: Flags.java,v 1.6 2005-09-15 03:49:43 salcianu Exp $
 */
public abstract class Flags {

    static boolean VERBOSE_TYPE_FILTER = false;

    public static boolean SHOW_INTRA_PROC_RESULTS = false;

    static boolean SHOW_INTRA_PROC_CONSTRAINTS = false;

    static boolean SHOW_TRIM_STATS = false;

    static boolean SHOW_METHOD_SCC = false;

    static boolean VERBOSE_CLONE = false;

    static boolean VERBOSE_ARRAYCOPY = false;

    static boolean VERBOSE_CALL = false;

    public static int MAX_INTRA_SCC_ITER = 1;

    public static boolean FLOW_SENSITIVITY = true;

    static boolean USE_FRESHEN_TRICK = true;

    static int MAX_CALLEES_PER_ANALYZABLE_SITE = 15;

    public static boolean RECORD_WRITES = false;
    public static boolean IGNORE_CERTAIN_MUTATIONS = true;
    public static boolean IGNORE_CONSTR_MUTATION_ON_THIS = true;

    /** If true, the whole-program analysis will eagerly execute and
        time all the pre-analysis: IR construction, call graph, etc.
        This allows the separation between pre-analysis and analysis
        time. */
    public static boolean TIME_PREANALYSIS = false;

    static List<Option> getOptions() {
	List<Option> opts = new LinkedList<Option>();
	opts.add(new Option("pa2:verbose-type-filter", "") {
	    public void action() {
		VERBOSE_TYPE_FILTER = true;
	    }});
	opts.add(new Option("pa2:show-intra-proc-results", "") {
	    public void action() {
		SHOW_INTRA_PROC_RESULTS = true;
	    }});
	opts.add(new Option("pa2:show-intra-proc-constraints", "") {
	    public void action() {
		SHOW_INTRA_PROC_CONSTRAINTS = true;
	    }});
	opts.add(new Option("pa2:show-trim-stats") {
	    public void action() {
		SHOW_TRIM_STATS = true;
	    }});
	opts.add(new Option("pa2:show-method-scc", "") {
	    public void action() {
		SHOW_METHOD_SCC = true;
	    }});
	opts.add(new Option("pa2:verbose-clone", "") {
	    public void action() {
		VERBOSE_CLONE = true;
	    }});
	opts.add(new Option("pa2:verbose-arraycopy", "") {
	    public void action() {
		VERBOSE_ARRAYCOPY = true;
	    }});
	opts.add(new Option("pa2:verbose-call", "") {
	    public void action() {
		VERBOSE_CALL = true;
		System.out.println("VERBOSE_CALL");
	    }});
	opts.add(new Option("pa2:max-intra-scc-iter", "<number>", "Coeficient used to compute the maximal number of iterations over a set of mutually recursive methods (an SCC in the call graph); after that number, we use an aggressive form of widening: we analyze each method from that SCC under the condition that all calls to same-SCC method is unanalyzable") {
	    public void action() {
		int old = MAX_INTRA_SCC_ITER;
		MAX_INTRA_SCC_ITER = Integer.parseInt(getArg(0));
		System.out.println("MAX_INTRA_SCC_ITER set to " + MAX_INTRA_SCC_ITER +
				   "; it was " + old);
	    }});
	opts.add(new Option("pa2:max-callees-per-site", "<number>", "The pointer analysis does not analyze CALLs with too many callees (default 15)") {
	    public void action() {
		MAX_CALLEES_PER_ANALYZABLE_SITE = Integer.parseInt(getArg(0));
		System.out.println("MAX_CALLEES_PER_ANALYZABLE_SITE set to " + MAX_INTRA_SCC_ITER);
	    }});
	opts.add(new Option("pa2:flow-insensitive", "Turn off the default pointer analysis flow sensitivity") {
	    public void action() {
		FLOW_SENSITIVITY = false;
	    }});
	opts.add(new Option("pa2:disable-freshen-trick", "Internal hack inside the pointer analysis; disable if you suspect some bug") {
	    public void action() {
		USE_FRESHEN_TRICK = false;
		System.out.println("DISABLE_FRESHEN_TRICK");
	    }});

	return opts;
    }
    
}