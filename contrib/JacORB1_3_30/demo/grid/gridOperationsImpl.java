package demo.grid;

import demo.grid.MyServerPackage.MyException;

public class gridOperationsImpl  
    implements MyServerOperations
{
    protected short height = 31;
    protected short width = 14;
    protected java.math.BigDecimal[][] mygrid;


    public gridOperationsImpl()
    {
	mygrid = new java.math.BigDecimal[height][width];
	for( short h = 0; h < height; h++ )
	    for( short w = 0; w < width; w++ )
		mygrid[h][w] = new java.math.BigDecimal("0.21");
    }

    public java.math.BigDecimal get(short n, short m)
    {
	if( ( n <= height ) && ( m <= width ) )
	    return mygrid[n][m];
	else
	    return new java.math.BigDecimal("0.01");
    }

    public short height()
    {
	// System.out.println("height: " + height );
	return height;
    }

    public void set(short n, short m, java.math.BigDecimal value)
    {
	if( ( n <= height ) && ( m <= width ) )
	    mygrid[n][m] = value;
    }

    public short width()
    {
	return width;
    }

    public short opWithException()
	throws MyException
    {
	throw new MyException("This is only a test exception, no harm done :-)");
    }






}


