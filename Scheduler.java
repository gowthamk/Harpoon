// Scheduler.java, created by cata
// Copyright (C) 2001 Catalin Francu <cata@mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.

package javax.realtime;
import java.util.HashSet;

/** An instance of <code>Scheduler</code> manages the execution of 
 *  schedulable objects and may implement a feasibility algorithm. The
 *  feasibility algorithm may determine if the known set of schedulable
 *  objects, given their particular execution ordering (or priority
 *  assignment), is a feasible schedule. Subclasses of <code>Scheduler</code>
 *  are used for alternative scheduling policies and should define an
 *  <code>instance()</code> class method to return the default
 *  instance of the subclass. The name of the subclass should be
 *  descriptive of the policy, allowing applications to deduce the
 *  policy available for the scheduler obtained via
 *  <code>getDefaultScheduler()</code> (e.g., <code>EDFScheduler</code>).
 */
public abstract class Scheduler {
    protected static Scheduler defaultScheduler = null;
    private VTMemory vt;
    
    /** Create an instance of <code>Scheduler</code>. */
    protected Scheduler() {
	addToRootSet();
	vt = new VTMemory();
    }

    /** Inform the scheduler and cooperating facilities that the resource
     *  demands (as expressed in the associated instances of
     *  <code>SchedulingParameters, ReleaseParameters, MemoryParameters</code>
     *  and <code>ProcessingGroupParameters</code>) of this instance of
     *  <code>Schedulable</code> will be considered in the feasibility analysis
     *  of the associated <code>Scheduler</code> until further notice. Whether
     *  the resulting system is feasible or not, the addition is completed.
     *
     *  @param schedulable A reference to the given instance of <code>Schedulable</code>.
     *  @return True, if the addition was successful. False, if not.
     */
    protected abstract void addToFeasibility(Schedulable schedulable);

    /** Trigger the execution of a schedulable object (like an
     *  <code>AsyncEventHandler</code>.
     *
     *  @param schedulable The Schedulable object to make active.
     */
    public abstract void fireSchedulable(Schedulable schedulable);

    /** Gets a reference to the default scheduler.
     *  In the RTJ spec, this is the PriorityScheduler, but we'll set it to whatever
     *  we wish to focus on at the moment, since this is a hot research target.
     *
     *  Currently, there's a PriorityScheduler (for compliance), and a 
     *  RoundRobinScheduler (for debugging).  Conceivably, one can put Schedulers 
     *  in a containment hierarchy, and getDefaultScheduler() would
     *  return the root.
     *
     *  @return A reference to the default scheduler.
     */
    public static Scheduler getDefaultScheduler() {
	if (defaultScheduler == null) {
	    setDefaultScheduler(RoundRobinScheduler.instance());
	    return getDefaultScheduler();
	}
	return defaultScheduler;
    }

    /** Gets a string representing the policy of <code>this</code>.
     *
     *  @return A <code>java.lang.String</code> object which is the name
     *          of the scheduling polixy used by <code>this</code>.
     */
    public abstract String getPolicyName();

    /** Queries the system about the feasibility of the set of scheduling
     *  and release characteristics currently being considered.
     */
    public abstract boolean isFeasible();
    protected abstract boolean isFeasible(Schedulable s, ReleaseParameters rp);

    /** Inform the scheduler and cooperating facilities that the resource
     *  demands (as expressed in the associated instances of
     *  <code>SchedulingParameters, ReleaseParameters, MemoryParameters</code>
     *  and <code>ProcessingGroupParameters</code>) of this instance of
     *  <code>Schedulable</code> should no longer be considered in the
     *  feasibility analysis of the associated <code>Scheduler</code>
     *  until further notice. Whether the resulting system is feasible
     *  or not, the subtraction is completed.
     *
     *  @return True, if the removal was successful. False, if the removal
     *          was unsuccessful.
     */
    protected abstract void removeFromFeasibility(Schedulable schedulable);

    /** Set the default scheduler. This is the scheduler given to instances
     *  of <code>RealtimeThread</code> when they are constructed. The default
     *  scheduler is set to the required <code>PriorityScheduler</code> at
     *  startup.
     *
     *  @param scheduler The <code>Scheduler</code> that becomes the default
     *                   scheduler assigned to new threads. If null nothing happens.
     */
    public static void setDefaultScheduler(Scheduler scheduler) {
	defaultScheduler = scheduler;
    }

    /** This method appears in many classes in the RTSJ and with various parameters.
     *  The parameters are either new scheduling characteristics for an instance of
     *  <code>Schedulable</code> or an instance of <code>Schedulable</code>. The
     *  method first performs a feasibility analysis using the new scheduling
     *  characteristics of either <code>this</code> or the given instance of
     *  <code>Schedulable</code>. If the resulting system is feasible the method
     *  replaces the current sheduling characteristics, of either <code>this</code>
     *  or the given instance of <code>Schedulable</code> as appropriate, with the
     *  new scheduling characteristics.
     *
     *  @param schedulable The instance of <code>Schedulable</code> to which the
     *                     parameters will be assigned.
     *  @param release The proposed release parameters.
     *  @param memory The proposed memory parameters.
     *  @return True, if the resulting system is feasible and the changes are made.
     *          False, if the resulting system is not feasible and no changes are made.
     */
    public abstract boolean setIfFeasible(Schedulable schedulable,
					  ReleaseParameters release,
					  MemoryParameters memory);

    /** This method appears in many classes in the RTSJ and with various parameters.
     *  The parameters are either new scheduling characteristics for an instance of
     *  <code>Schedulable</code> or an instance of <code>Schedulable</code>. The
     *  method first performs a feasibility analysis using the new scheduling
     *  characteristics of either <code>this</code> or the given instance of
     *  <code>Schedulable</code>. If the resulting system is feasible the method
     *  replaces the current sheduling characteristics, of either <code>this</code>
     *  or the given instance of <code>Schedulable</code> as appropriate, with the
     *  new scheduling characteristics.
     *
     *  @param schedulable The instance of <code>Schedulable</code> to which the
     *                     parameters will be assigned.
     *  @param release The proposed release parameters.
     *  @param memory The proposed memory parameters.
     *  @param group The proposed processing group parameters.
     *  @return True, if the resulting system is feasible and the changes are made.
     *          False, if the resulting system is not feasible and no changes are made.
     */

    public abstract boolean setIfFeasible(Schedulable schedulable,
					  ReleaseParameters release,
					  MemoryParameters memory,
					  ProcessingGroupParameters group);

    /** Chooses a thread to run */
    protected abstract long chooseThread(long currentTime);

    /** Adds a thread to the thread list */
    protected abstract void addThread(RealtimeThread thread);

    /** Removes a thread from the thread list */
    protected abstract void removeThread(RealtimeThread thread);

    /** Any threads running? */
    protected abstract boolean noThreads();

    /** Stop running <code>threadID</code> until enableThread - 
     *  used in the lock implementation to wait on a lock.
     */
    protected abstract void disableThread(long threadID);

    /** Enable <code>threadID</code>, allowing it run again - used in notify */
    protected abstract void enableThread(long threadID);

    /** Cause the thread to block until the next period */
    protected abstract void waitForNextPeriod(RealtimeThread rt);

    /** Switch every <code>microsecs</code> microseconds */
    protected final native void setQuanta(long microsecs);

    /** Print out the status of the scheduler */
    public final static void print() {
	Scheduler sched = RealtimeThread.currentRealtimeThread().getScheduler();
	if (sched == null) {
	    sched = Scheduler.getDefaultScheduler();
	}
	NoHeapRealtimeThread.print("\n"+sched.getPolicyName()+": "+sched);
    }

   /** Run the runnable in an atomic section */
    public final static void atomic(Runnable run) {
	int state = beginAtomic();
	run.run();
	endAtomic(state);
    }

    private final void addToRootSet() {
	if (Math.sqrt(4)==0) {
	    chooseThread(0);
	    noThreads();
	    jDisableThread(null, 0);
	    jEnableThread(null, 0);
	    jChooseThread(0);
	    (new RealtimeThread()).schedule();
	    (new RealtimeThread()).unschedule();
	    new NoSuchMethodException();
	    new NoSuchMethodException("");
	    print();
	}
    }

    final void addThreadToLists(final RealtimeThread thread) {
	atomic(new Runnable() {
	    public void run() {
		addToFeasibility(thread);
		ImmortalMemory.instance().enter(new Runnable() {
		    public void run() {
			addThreadInC(thread, thread.getUID());
		    }
		});
		addThread(thread);
	    }
	});
    }

    final void removeThreadFromLists(final RealtimeThread thread) {
	atomic(new Runnable() {
	    public void run() {
		removeThread(thread);
		removeThreadInC(thread);
		removeFromFeasibility(thread);
	    }
	});
    }

    private final native void addThreadInC(Schedulable t, long threadID);
    private final native long removeThreadInC(Schedulable t);
    private final native static int beginAtomic();
    private final native static void endAtomic(int state);

    final static void jDisableThread(final RealtimeThread rt, 
				     final long threadID) {
	atomic(new Runnable() {
	    public void run() {
		Scheduler sched;
		if (rt != null) { // Is this really necessary?
		    sched = rt.getScheduler();
		} else {
		    sched = getDefaultScheduler();
		}
		if (sched != null) {
		    sched.disableThread(threadID);
		} 
	    }
	});
	
    }
    
    final static void jEnableThread(final RealtimeThread rt, 
				    final long threadID) {
	atomic(new Runnable() {
	    public void run() {
		Scheduler sched;
		if (rt != null) { // Is this really necessary?
		    sched = rt.getScheduler();
		} else {
		    sched = getDefaultScheduler();
		}
		if (sched != null) {
		    sched.enableThread(threadID);
		}
	    }	    
	});
    }

    long temp;

    final protected long jChooseThread(final long currentTime) {
	vt.enter(new Runnable() {
	    public void run() {
		Scheduler.this.temp = chooseThread(currentTime);
	    }
	});
	return temp;
    }
}