package javax.realtime;

/** The <code>PhysicalMemoryManager</code> is available for use
 *  by the various physical memory accessor objects
 *  (<code>VTPhysicalMemory, LTPhysicalMemory, ImmortalPhysicalMemory,
 *  RawMemoryAccess, RawMemoryFloatAccess</code>) to create objects
 *  of the correct type that are bound to areas of physical memory
 *  with the appropriate characteristics -- or with appropriate
 *  accessor behavior. Esxamples of characteristics that might be
 *  specified are: DMA memory, accessors with byte swapping, etc.
 *  <p>
 *  The base implementation will provide a <code>PhysicalMemoryManager</code>
 *  and a set of <code>PhysicalMemoryTypeFilter</code> classes that correctly
 *  identify memory classes that are standard for the (OS, JVM, and processor)
 *  platform.
 *  <p>
 *  OEMs may provide a <code>PhysicalMemoryTypeFilter</code> classes that allow
 *  additional characteristics of memory devices to be specified.
 *  <p>
 *  Memory attributes that are configured may not be compatible with one another.
 *  For instance, copy-back cache enable may be imcompatible with execute-only.
 *  In this case, the implementation of memory filters may detect conflicts and
 *  throw a <code>MemoryTypeConflictException</code>, but since filters are not
 *  part of the normative RTSJ, this exception is at best advisory.
 */
public final class PhysicalMemoryManager {
    /** Specify this to identify aligned memory. */
    public static final String ALIGNED = "ALIGNED";

    /** Specify this if byte swapping should be used. */
    public static final String BYTESWAP = "BYTESWAP";

    /** Specify this to identify DMA memory. */
    public static final String DMA = "DMA";

    /** Specify this to identify shared memory. */
    public static final String SHARED = "SHARED";


    public PhysicalMemoryManager() {}

    /** Query the system about the removability of the specified range
     *  of memory.
     */
    public static boolean isRemovable(long address, long size) {
	// TODO

	return false;
    }

    /** Query the system about the removed state of the specified range
     *  of memory. This method is used for devices that lien in the
     *  memory address space and can be removed while the system is
     *  running (such as PC cards).
     */
    public static boolean isRemoved(long address, long size) {
	// TODO

	return false;
    }

    /** Register the specified <code>AsyncEventHandler</code> to run
     *  when any memory in the range is added to the system.
     */
    public static void onInsertion(long base, long size,
				   AsyncEventHandler aeh) {
	// TODO
    }

    /** Register the specified <code>AsyncEventHandler</code> to run
     *  when any memory in the range is removed from the system.
     */
    public static void onRemoval(long base, long size,
				 AsyncEventHandler aeh)
	throws IllegalArgumentException {
	// TODO
    }

    /** Register a memory type filter with the physical memory manager. */
    public static final void registerFilter(Object name,
					    PhysicalMemoryTypeFilter filter)
	throws DuplicateFilterException, IllegalArgumentException {
	// TODO
    }

    /** Remove the identified filter from the set of registered filters. */
    public static final void removeFilter(Object name) {
	// TODO
    }
}