import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;

public class Process {
    public static void main(String args[]) {
	BufferedReader buf = new BufferedReader(new InputStreamReader(System.in));
	try {
	    String st;
	    long lasttime = 0;
	    long lastid = 0;
	    long li = 0;
	    while ((st = buf.readLine())!=null) {
		if (st.indexOf("Scheduler.sleep")!=-1) {
		    String[] sbuf = st.split("[\\\\(\\\\)\\\\,]");
		    System.out.println(sbuf[3]);
		    
		} else if (st.indexOf("ChooseThread")!=-1) {
		    String[] sbuf = st.split("[\\\\(\\\\)\\\\=]");
		    long threadNum = Long.parseLong(sbuf[0].trim())-1;
		    if (threadNum == 0) continue;
		    
		    String[] sbuf2 = sbuf[3].split("s,");
		    String[] sbuf3 = sbuf2[1].split("us");
		    long time = Long.parseLong(sbuf2[0].trim())*1000000;
		    time += Long.parseLong(sbuf3[0].trim());
		    
		    if (lastid != threadNum) {
			if ((lasttime!=0)&&(time>lasttime)) {
			    long t = (time-lasttime)/1000;
			    long i;
			    for (i = 0; i < lastid; i++) {
				System.out.print("X");
			    }
			    for (; i <= 5; i++) {
				System.out.print(" ");
			    }
			    System.out.println(t);
// 	                    if ((++li)%10==0) {
// 			        System.out.println("-------------");
// 			    }
			    t = (t + 49) / 100;
			    for (i = 1; i < t; i++) {
				for (long j = 0; j < lastid; j++) {
				    System.out.print("X");
				}
				System.out.println();
// 			        if ((++li)%10==0) {
// 				    System.out.println("-------------");
// 			        }
			    }
			}
			lasttime = time;
			lastid = threadNum;
		    }		    
		}
	    }		
	} catch (IOException e) {
	    System.out.println(e.toString());
	    System.exit(-1);
	}
    }
}
